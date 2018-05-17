#! /usr/bin/env python3

import configparser
import argparse
import sys
import ipaddress
import datetime
import os
from pathlib import Path

try:
    import boto3
except ImportError:
    print("FATAL: 'boto3' python3 module not available. Please install it with your package manager or pip3. Exiting.")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("FATAL: 'requests' python3 module not available. Please install it with your package manager or pip3. Exiting.")
    sys.exit(1)

def main(argv):
    argList = buildArgParser(argv)
    
    ipAddr = str(getIP())
    readLastKnownIP(argList.ipLogFilePath, ipAddr)
    
    configDict = parseConfig(argList)
    
    if argList.dryrun == True:
        dryRunOutput(configDict, ipAddr)
        sys.exit(0)
        
    updateRecord(configDict, ipAddr)

    logCurrentIP(argList.ipLogFilePath,ipAddr)

def buildArgParser(argv):
    parser = argparse.ArgumentParser(description="Update a Route53 DNS record based upon current public IP.")
    parser.add_argument('--config',
                        dest="configFilePath",
                        default=None,
                        help="Path to the configuration file for the current run. \
                        If this is set, we will ignore the other config options except for --iplog.")

    parser.add_argument("--iplog",
                        dest="ipLogFilePath", 
                        default="/app/elasticdns.ip", 
                        help="Path to where the previous ip should be stored.\
                        Defaults to /app/elasticdns.ip")
    
    parser.add_argument("--zone-id",
                        dest="zone_id",
                        default="",
                        help="The Route53 Hosted Zone Id to reference.\
                        Example: 'AAAAAAAAAAAAAA' ")
                        
    parser.add_argument("--record",
                        dest="record_set",
                        default="",
                        help="The Resource Record Set inside the hosted zone.\
                        Example: 'test.example.com' ")
    
    parser.add_argument("--type",
                        dest="record_type", 
                        default="A", 
                        help="The record type we are updating. Currently defaults to 'A'.\
                        AAAA unsupported at this time.")
    
    parser.add_argument("--ttl",
                        dest="record_ttl", 
                        default="300", 
                        help="The record's TTL in seconds. Defaults to 300 seconds.")
    
    parser.add_argument("--profile",
                        dest="profile", 
                        default="", 
                        help="Only useful if you've set up ~/.aws/credentials file. \
                        If so, use this to pick which IAM profile is used by boto3. \
                        Defaults to the 'default' profile.")
    
    parser.add_argument("--comment",
                        dest="comment", 
                        default="Updating record at: " + str(datetime.datetime.now()), 
                        help="An optional comment for the update. Defaults to current date and time.")
    
    parser.add_argument('--dryrun', 
                        dest="dryrun",
                        action="store_true",
                        help="Turns on dryrun mode. Dryrun mode will output the changes that would be made without actually making them.")

    return parser.parse_args()

def parseConfig(argList):
    
    if argList.configFilePath == None:
        configDict = parseConfigArgs(argList)
    else:
        if Path(argList.configFilePath).is_file():
            configDict = parseConfigFile(argList.configFilePath)
        else:
            print("A config path was provided, but the file specified cannot be found. We are bailing out to be safe.")
            sys.exit(1)
                
    sanityCheckConfig(configDict)
    
    return configDict

def parseConfigFile(configFilePath):
    if Path(configFilePath).is_file():
        config = configparser.ConfigParser()
        config.read(configFilePath)

        recordHeader = config.sections()[0]

        configDict = {
                  "HostedZoneId": config[recordHeader]["HostedZoneId"],
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

def parseConfigArgs(argList):
    configDict = {
        "HostedZoneId": str(argList.zone_id),
        "RecordSet": str(argList.record_set),
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
        print("The last IP that was logged matches our current public IP. Assuming records are up to date. Exiting.")
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
        botoSession = boto3.Session()
    else:
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

def dryRunOutput(configDict, ipAddr):
    print("Our validated IP is:", ipAddr)
    
    for key, value in configDict.items():
        print(key," = ", value)
    
    return 0
    
if __name__ == "__main__":
   main(sys.argv[1:])