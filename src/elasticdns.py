#! /usr/bin/env python3

import logging
import sys
import ipaddress
import os
import boto3
import requests
from threading import Event
import signal


should_quit = Event()
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def main():
    hosted_zone_id: str = os.environ["ELASTICDNS_HOSTZONE_ID"]
    record_set_name: str = os.environ["ELASTICDNS_RECORD_SET"]
    record_set_type: str = os.getenv("ELASTICDNS_RECORD_TYPE", "A")
    record_set_ttl: int = int(os.getenv("ELASTICDNS_TTL", "300"))
    update_comment: str = os.getenv("ELASTICDNS_COMMENT", "")

    aws_profile: str = os.getenv("ELASTICDNS_AWS_PROFILE", "")

    if aws_profile:
        session = boto3.Session(profile_name=aws_profile)
    else:
        session = boto3.Session()

    sts = session.client("sts")
    route53 = session.client("route53")

    last_updated_ip = None

    logger.info("Testing provided/discovered credentials by calling sts:GetCallerIdentity()")
    logger.info(sts.get_caller_identity())

    while not should_quit.is_set():
        current_ip = get_current_ip("https://checkip.amazonaws.com")
        logger.info(f"Received back IP address: {current_ip}")

        if validate_ip(current_ip):
            if last_updated_ip == current_ip:
                pass
            else:
                resource_records = [{"Value": current_ip}]

                r53_update_record(
                    route53,
                    hosted_zone_id=hosted_zone_id,
                    change_comment=update_comment,
                    record_set_name=record_set_name,
                    record_type=record_set_type,
                    record_ttl=record_set_ttl,
                    resource_records=resource_records
                )

                last_updated_ip = current_ip

        should_quit.wait(60)

    sys.exit(0)


def validate_ip(address):
    try:
        ipaddress.ip_address(address)
    except ValueError:
        raise Exception("Response does not pass validation: ", address)

    return True


def get_current_ip(checkip_url: str):
    try:
        response = requests.get(checkip_url)
    except ConnectionError:
        raise Exception(f"Connection to '{checkip_url}' failed.")
    except TimeoutError:
        raise Exception(f"Connection to '{checkip_url}' timed out.")

    response = response.text.strip("\n")
    
    return response


def r53_update_record(client,
                      *,
                      hosted_zone_id: str,
                      change_comment: str,
                      record_set_name: str,
                      record_type: str, 
                      record_ttl: int,
                      resource_records: list
                      ):
  
    client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Comment": change_comment,
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": record_set_name,
                        "Type": record_type,
                        "TTL": record_ttl,
                        "ResourceRecords": resource_records,
                    },
                }
            ],
        },
    )


def quit(signo, _frame):
    logging.info(f"Interrupted by {signo}, shutting down")
    should_quit.set()
    

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, quit)
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGHUP, quit)

    main()