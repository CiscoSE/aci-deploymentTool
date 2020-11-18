__license__ = """
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
__status__ = "Demonstration only - Not maintained"

import sys
import os
import argparse
import getpass



#Append path for files in the bin directory
sys.path.append(os.getcwd() + '/bin')

#Import URL functions from the common.py file. We use these for all API communication
from common import urlFunctions
from common import loggingFunctions

#clear the terminal window before we continue
os.system('clear')

#########################
# Argument Handling
#########################

#Default values
defaultProcessedFolder = './processedFolder/'   # Source files successfully processed are moved to this folder to prevent them from being run more then once.
defaultSourceFolder = './sourceFolder/'
defaultPassword = 'DefaultPassword'             #TODO Make this go away...Prompt for password at the start of the script.  
defaultAPIC = "10.82.66.225"
defaultUser = "admin"

helpMsg = """
Deployment Tool for pushing XML configuration files for Cisco ACI APICs. 
"""

argsParse = argparse.ArgumentParser(description=helpMsg)
argsParse.add_argument('-a', '--APIC',             action='store', dest='apic',          default=defaultAPIC,            help='APIC IP addresses or FQDN to be changed.' )
argsParse.add_argument('-u', '--user',             action='store', dest='user',            default=defaultUser,            help='User name for APIC Access' )
argsParse.add_argument('-p', '--password',         action='store', dest='password',        default=defaultPassword,        help='Password for APIC Access' )
argsParse.add_argument('-f', '--source-folder',    action='store', dest='sourceFolder',    default=defaultSourceFolder,    help='Source location for changes to be made' )
argsParse.add_argument('-P', '--processed-folder', action='store', dest='processedFolder', default=defaultProcessedFolder, help='Location for files that have been processed' )
args = argsParse.parse_args()

# Functions
def main():
    # Initialize API access object
    URL = urlFunctions(args)
    #Get Cookie
    cookie = URL.getCookie(args.user, args.password)['APIC-cookie']
    locateFiles()
    return

def locateFiles():
    #Check for sourceFolder
    if os.path.isdir(args.sourceFolder) == 'False':
        loggingFunctions().writeEvent(msg="Source Directory was not found. Checking default folder", msgType="WARN")
    
    return

def checkFolderStructure():
    # Does the source folder exist? Cannot continue without it, but we will create one and tell where we put it.
    # Does the processed folder exist? Make it does if it is not there already.

    return

main()