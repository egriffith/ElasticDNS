#! /usr/bin/env python3

import logging
import argparse
import sys
import ipaddress
import datetime
import os
import time

try:
    import boto3
except ImportError:
    raise ImportError("FATAL: 'boto3' python3 module not available. Please install it with your package manager or pip3. Exiting.")


try:
    import requests
except ImportError:
    raise ImportError("FATAL: 'requests' python3 module not available. Please install it with your package manager or pip3. Exiting.")


def main(argv):
    def container_main(config):
        while True:
            ipAddr = str(getIP())
            readLastKnownIP(config["IpLogFile"], ipAddr)
            updateRecord(config, ipAddr)
            logCurrentIP(config["IpLogFile"], ipAddr)
            time.sleep(int(config["SleepTimer"]))

    arglist = buildArgParser(argv)

    config = parseConfigEnv()

    if arglist.inContainer:
        container_main(config)
    else:
        ipAddr = str(getIP())
        readLastKnownIP(config["IpLogFile"], ipAddr)
        updateRecord(config, ipAddr)
        logCurrentIP(config["IpLogFile"], ipAddr)


def buildArgParser(argv):
    parser = argparse.ArgumentParser(description="Update a Route53 DNS record based upon current public IP.")

    parser.add_argument("--container",
                        dest="inContainer",
                        action="store_true",
                        default=False)

    parser.add_argument('--dryrun',
                        dest="dryrun",
                        action="store_true",
                        help="Turns on dryrun mode. Dryrun mode will output the changes that would be made without actually making them.")

    return parser.parse_args()


def parseConfigEnv():
    conf = dict()
    conf["HostedZoneId"] = os.getenv("ELASTICDNS_HOSTZONEID")
    conf["RecordSet"] = os.getenv("ELASTICDNS_RECORDSET")
    conf["Type"] = os.getenv("ELASTICDNS_RECORDTYPE")
    conf["TTL"] = os.getenv("ELASTICDNS_TTL", "600")
    conf["Profile"] = os.getenv("ELASTICDNS_PROFILE")
    conf["Comment"] = os.getenv("ELASTICDNS_COMMENT")
    conf["SleepTimer"] = os.getenv("ELASTICDNS_SLEEP_SECONDS")
    conf["IpLogFile"] = os.getenv("ELASTICDNS_IPLOG")

    if conf["HostedZoneId"] == "" or conf["HostedZoneId"] is None:
        raise Exception("HostedZoneId input was blank or empty. Script cannot continue.")

    if conf["RecordSet"] == "" or conf["RecordSet"] is None:
        raise Exception("RecordSet input was blank or empty. Script cannot continue.")

    if conf["Type"] == "" or conf["Type"] is None:
        raise Exception("RecordType input was blank or empty. Script cannot continue.")

    if conf["TTL"] == "" or conf["TTL"] is None:
        conf["TTL"] = 600

    if conf["SleepTimer"] == "" or conf["SleepTimer"] is None:
        conf["SleepTimer"] = 300

    if conf["Comment"] == "" or conf["Comment"] is None:
        conf["Comment"] = "Record last updated at: " + str(datetime.datetime.now())

    if conf["IpLogFile"] == "" or conf["IpLogFile"] is None:
        conf["IpLogFile"] = "/var/log/elasticdns/elasticdns.ip"

    return conf



def parseConfigArgs(argList):
    configDict = {
        "HostedZoneId": str(argList.zone),
        "RecordSet": str(argList.record),
        "TTL": int(argList.record_ttl),
        "Type": str(argList.record_type),
        "Profile": str(argList.profile),
        "Comment": str(argList.comment)
    }
    
    return configDict

def sanityCheckConfig(configDict):
    if configDict['HostedZoneId'] == "" or configDict['RecordSet'] == "":
        print("Either HostedZone or RecordSet are blank. These are mandatory and do not have default values.\n\
        Please make sure they are configured either via arguements or a valid config file.\n\
        Exitting.")
        
        sys.exit(1)

def logCurrentIP(ipLogFilePath, ipAddr):
    os.makedirs(os.path.dirname(ipLogFilePath), exist_ok=True)
    with open(ipLogFilePath, "w") as ipLog:
        ipLog.write(ipAddr)


def readLastKnownIP(ipLogFilePath, newIP):
    try:
        with open(ipLogFilePath, 'r') as ipLog:
            oldIP = ipLog.read()
    except FileNotFoundError:
        oldIP = "(blank)"

    if oldIP == newIP:
        print("The last IP that was logged matches our current public IP. Assuming records are up to date.")
    else:
        print("New IP: ", newIP, " does not match previous IP: ", oldIP, ", Updating records.")
        return 0


def getIP():

    def validateIP(address):
        try:
            ipaddress.ip_address(address)
        except ValueError:
            print("Response does not pass validation: ", address)
            return False

        return True

    try:
        response = requests.get('https://checkip.amazonaws.com')
    except ConnectionError:
            raise Exception("Connection to https://checkip.amazonaws.com failed.")
    except TimeoutError:
            raise Exception("Connection to https://checkip.amazonaws.com timed out.")

    response = response.text.strip("\n")

    if validateIP(response) is True:
        print("Our current IP is: ", response)
        return response
    else:
        raise Exception("IP we received from 'https://checkip.amazonaws.com' did not pass validation.")


def updateRecord(configDict, ipAddr):
    if configDict['Profile'] == "" or configDict['Profile'] == None:
        botoSession = boto3.Session()
    else:
        botoSession = boto3.Session(profile_name=configDict['Profile'])
        
    client = botoSession.client("route53")
    response = client.change_resource_record_sets(
    HostedZoneId=configDict['HostedZoneId'],
    ChangeBatch={
        'Comment': str(configDict['Comment']),
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': str(configDict['RecordSet']),
                    'Type': str(configDict['Type']),
                    'TTL': int(configDict['TTL']),
                    'ResourceRecords': [
                        {
                            'Value': str(ipAddr)
                        },
                    ],
                }
            },
            ]
        }
    )

    return 0


def dryRunOutput(configDict, ipAddr):
    print("Our validated IP is:", ipAddr)
    
    for key, value in configDict.items():
        print(key," = ", value)


if __name__ == "__main__":
    main(sys.argv[1:])
