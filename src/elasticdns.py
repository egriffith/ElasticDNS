#! /usr/bin/env python3

import boto3
import configparser
import argparse
import sys
import requests
import ipaddress
import datetime
from pathlib import Path

def main(argv):
    arglist = buildArgParser(argv)
    
    ipAddr = str(getIP())
    readLastKnownIP(arglist.ipLogFilePath, ipAddr)
    
    configDict = parseConfig(arglist.configFilePath)
    updateRecord(configDict, ipAddr)


    logCurrentIP(arglist.ipLogFilePath,ipAddr)

def buildArgParser(argv):
    parser = argparse.ArgumentParser(description="Update a Route53 DNS record based upon current public IP.")
    parser.add_argument('--config', '-c', dest="configFilePath", default="/etc/elasticdns/elasticdns.conf", help="Path to the configuration file for the current run.")
    parser.add_argument("--iplog", "-i", dest="ipLogFilePath", default="/var/log/elasticdns/elasticdns.ip", help="Path to where the previous ip should be stored.")

    return parser.parse_args()

def parseConfig(configFilePath):
    if Path(configFilePath).is_file():
        config = configparser.ConfigParser()
        config.read(configFilePath)

        recordHeader = config.sections()[0]

        configDict = {"HostedZoneId": config[recordHeader]["HostedZoneId"],
                  "RecordSet": config[recordHeader]["RecordSet"],
                  "TTL": int(config[recordHeader]["TTL"]),
                  "Type": config[recordHeader]["Type"],
                  "Profile": config[recordHeader]["Profile"],
                  "Comment": config[recordHeader]["Comment"]          
                }
    
        return configDict

    else:
        print("Config file not found at path: ", configFilePath, ". Exiting.")
        sys.exit(1)

def logCurrentIP(ipLogFilePath, ipAddr):
    with open(ipLogFilePath, "w") as ipLog:
        ipLog.write(ipAddr)

def readLastKnownIP(ipLogFilePath, newIP):
    try:
        with open(ipLogFilePath, 'r') as ipLog:
            oldIP = ipLog.read()
    except FileNotFoundError:
        oldIP = "(blank)"

    if oldIP == newIP:
        print("The last IP that was logged matches our current public IP. Assuming records are up to date. Exitting.")
        sys.exit(0)
    else:
        print("New IP: ", newIP, " does not match previous IP: ", oldIP, ", Updating records.")
        return 0

def getIP():
    try:
        response = requests.get('https://checkip.amazonaws.com')
    except ConnectionError:
            print("Connection to https://checkip.amazonaws.com failed.")
            sys.exit(1)
    except TimeoutError:
            print("Connection to https://checkip.amazonaws.com timed out.")
            sys.exit(1)

    response = response.text.strip("\n")

    if validateIP(response) == True:
        print("Our current IP is: ", response)
        return response
    else:
        sys.exit(1)

def validateIP(address):
    try:
        ipaddress.ip_address(address)
    except ValueError:
        print("Response does not pass validation: ", address)
        return False

    return True

def updateRecord(configDict, ipAddr):
    if configDict['Comment'] == "":
        configDict['Comment'] = "Updating record at: " + str(datetime.datetime.now())

    if configDict['Profile'] == "":
        configDict['Profile'] = "default"

    botoSession = boto3.Session(profile_name=configDict['Profile'])
    client = botoSession.client("route53")
    response = client.change_resource_record_sets(
    HostedZoneId=configDict['HostedZoneId'],
    ChangeBatch={
        'Comment': configDict['Comment'],
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': configDict['RecordSet'],
                    'Type': configDict['Type'],
                    'TTL': configDict['TTL'],
                    'ResourceRecords': [
                        {
                            'Value': ipAddr
                        },
                    ],
                }
            },
            ]
        }
    )
    return 0

if __name__ == "__main__":
   main(sys.argv[1:])