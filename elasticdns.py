#! /usr/bin/which python3

import boto3
import socket
import configparser
import argparse
import sys
import requests
import ipaddress

def main(argv):
    parser = argparse.ArgumentParser(description="Update a Route53 DNS record based upon current public IP.")
    parser.add_argument('--config', '-c', dest="configFilePath", default="elasticdns.conf", help="Path to the configuration file for each run.")
    parser.add_argument("--log-file", "-l", dest="logFilePath", default="/var/log/elasticdns.log", help="Path to the log file")
    arglist = parser.parse_args("".split())
    
    global logPath 
    logPath = arglist.logFilePath

    readConfig(arglist.configFilePath)
    ipAddr = getIP()
    #updateRecord(ipAddr)

def readConfig(configFilePath):
    config = configparser.ConfigParser()
    config.read(configFilePath)
    #for section in config.keys():
    #    print(section)
    #print(logPath)
    #print(config['DEFAULT']['AccessKey'])
    #print(config['DEFAULT']['SecretKey'])
    #print(config['DEFAULT']['RecordID'])

def getIP():
    response = requests.get('https://checkip.amazonaws.com')
    print("getIP received:", response.text)
    response = response.strip("\n")
    validateIP(response.text)
    #if validateIP(str(response.text)) == True:
    #    return response
    #else:
    #    print("ERROR: Did not get back a valid IP. Response was:", response.text)
    #    sys.exit(1)

def validateIP(address):
    address = (str(address).strip("\n"))
    print("validateIP received:", address)
    #try:
    print(ipaddress.ip_address(address))
    #except ValueError:
    #    print('address is invalid for IPv4:', address)
    #    return False

    return 0

def updateRecord():
    return 0

def log(logMSG):
    return 0

if __name__ == "__main__":
   main(sys.argv[1:])