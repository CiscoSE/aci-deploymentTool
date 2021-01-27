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
import re
import ntpath
import textwrap         # Requires Python 3.3 or later. 



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
def getPassword():
    print("Enter Password")
    return getpass.getpass()

argsParse = argparse.ArgumentParser(description=helpMsg)
argsParse.add_argument('-a', '--APIC',             action='store',       dest='apic',            default=defaultAPIC,            help='APIC IP addresses or FQDN to be changed.' )
argsParse.add_argument('-u', '--user',             action='store',       dest='user',            default=defaultUser,            help='User name for APIC Access' )
argsParse.add_argument('-p', '--password',         action='store',       dest='password',        default=getPassword(),          help='Password for APIC Access' )
argsParse.add_argument('-f', '--source-folder',    action='store',       dest='sourceFolder',    default=defaultSourceFolder,    help='Source location for changes to be made' )
argsParse.add_argument('-P', '--processed-folder', action='store',       dest='processedFolder', default=defaultProcessedFolder, help='Location for files that have been processed')
argsParse.add_argument('--fail-safe',              action='store_true', dest='failSafe',                                        help='This line is required in order to make changes')
args = argsParse.parse_args()

# Functions
def main():
    # Initialize API access object
    URL = urlFunctions(args)
    #Get Cookie
    cookie = URL.getCookie(args.user, args.password).cookies
    fullFileList = processFiles()
    for file in fullFileList:
        processFile(xmlFile=file, cookie=cookie)
    return

def processFiles():
    #Validate the directories are there and create them if they are not. If we don't have directories, we don't need to continue.
    validateDirectory(Folder=args.sourceFolder, defaultFolderName=defaultSourceFolder, title="Source")
    validateDirectory(Folder=args.processedFolder, defaultFolderName=defaultProcessedFolder, title="Processed",failureAction="WARN")

    #Get files and process
    return getFileList(args.sourceFolder)    

def getFileList(sourceFolder):
    #TODO Add sort so that if files need to be processed in a specific order that is possible through the naming of the files. 
    loggingFunctions().writeEvent(msg="Getting files from source folder")
    listOfFiles = os.listdir(sourceFolder)
    if (len(listOfFiles)) == 0:
        loggingFunctions().writeEvent(msg=f"No files found in {listOfFiles}", msgType='FAIL')
    else:
        fileCount = len(listOfFiles)
        if fileCount == 1:
            loggingFunctions().writeEvent(msg=f"{fileCount} file found")
        else:
            loggingFunctions().writeEvent(msg = f"{fileCount} files found")
    fullFileList = normalizeFileList(listOfFiles = listOfFiles, relativePath = sourceFolder)
    #Verify that we get back the same number of files that we sent to normalization
    if (len(fullFileList)) != (len(listOfFiles)):
        loggingFunctions().writeEvent(msg = f"Found {len(listOfFiles)}, but only normalized {len(fullFileList)}. Script cannot continue",msgType = 'FAIL')
    else:
        loggingFunctions().writeEvent(msg=f"Files Successfully Normalized: {len(fullFileList)}")
    return fullFileList

def processFile(xmlFile, cookie):
    URL = urlFunctions(args)
    loggingFunctions().writeEvent(msg=f"Processing file: {xmlFile}")
    thisFileRAW = open(xmlFile, 'r')
    #This must be the DN comment line. The file cannot be processed without this.
    regexSearchResult = (re.search(' (dn=.*) ', thisFileRAW.readline()))
    if regexSearchResult is None:
        #We don't have a DN, so we cannot continue
        loggingFunctions().writeEvent(msg="\tNo DN Found in this file. Processing of this file cannot continue.", msgType='WARN')
        handleDnFailure()
        exit()
    dn = f"{regexSearchResult.group(1)}".split('=',1)[1]

    #TODO One day we might want to validate the DNs with known classes and warn if the DNs or classes don't make sense.
    loggingFunctions().writeEvent(msg=f'\tDN Found: {dn}')

    #Format a URL with the APIC address and DN 
    url = makeURL(dn)
    loggingFunctions().writeEvent(f"url: {url}")

    #Read remaining lines of the current file. We are not validating this xml. It will either work or it wont.
    data = thisFileRAW.readlines()
    
    #Headers need to include cookie
    header={"Content-Type": "application/xml", "APIC-cookie": f"{cookie}"}
    
    # Print URL and header
    loggingFunctions().writeEvent

    if args.failSafe == False:
        loggingFunctions().writeEvent("\t########## FAILSAFE ENABLED - No Changes Will be Made ##########\n\n", "WARN")
        print(f"\tTarget URL:\t\t{url}\n\n")
        print(f"\tHeader:\t\t{header}")
        print(f"\tData To Send:\n{data}")
        #Output values only
    else:
        #Write the change to the Apic
        changeResult = URL.getData(htmlMethod="POST", data=data, url=url, headers=header, cookies=cookie)
        fileToMove = thisFileRAW.name
        thisFileRAW.close
        os.rename(f'{fileToMove}', f'{args.processedFolder}{ntpath.basename(fileToMove)}')
        loggingFunctions().writeEvent('Moved {fileToMove} to {args.processedFolder}', "INFO")
        URL.httpErrorReporting(status=changeResult.status_code, reason=changeResult.reason, msgType='WARN')
        print(f"Change Result:\t{changeResult.text}")
    return

def makeURL(dn, dataType='xml', moClass="mo"):
    return f"https://{args.apic}/api/{moClass}/{dn}.{dataType}"

def handleDnFailure():
    #Simple routine to handle yes or no input. 
    #TODO Wold be better if this routine just returned true or false so I could use it elsewhere without modification. 
    while True:
        question = input('\nDo you want to continue to process other files if they remain?\n')

        if re.search('^[Nn]$|^[Nn][Oo]$', question):
            loggingFunctions().writeEvent(msg="Script will exit",msgType='FAIL')
            exit()
        elif re.search('^[Yy][Ee][Ss]$|^[Yy]$', question):
            loggingFunctions().writeEvent(msg="Script Will Continue")
            break
    return


def normalizeFileList(listOfFiles, relativePath):
    #TODO Process each file name provided and append the full path to it.

    #Converting to a full path if it isn't already that way.
    if relativePath.startswith('/') == False:
        relativePath = os.path.abspath(relativePath)
        loggingFunctions().writeEvent(msg=f"Absolute Path: {relativePath}")
    #Prepositioning the slash at the end of the path if it is not already there. 
    if relativePath.endswith('/') == False:
        relativePath = relativePath + '/'
    loggingFunctions().writeEvent(msg=f"Normalized Path: {relativePath}")
    #Loop through all file names and define the full path
    returnPaths = []
    for file in listOfFiles:
        returnPaths.append(relativePath + file)
    return returnPaths

def validateDirectory(Folder, defaultFolderName, title, failureAction='FAIL'):
    #Check for sourceFolder
    loggingFunctions().writeEvent(msg=f"Checking Source Folder:\tsourceFolder")
    if (os.path.isdir(Folder)) == False:
        loggingFunctions().writeEvent(msg=f"{title} Directory was not found. Checking default folder", msgType="WARN")
        if (defaultFolderName == Folder) and  (os.path.isdir(defaultFolderName) == False):
            # We will create the source folder and tell the user to use that folder.
            os.mkdir(defaultFolderName)
            loggingFunctions().writeEvent(msg=f"{title} directory not found. New Folder created here: {Folder}", msgType=failureAction)
            exit()
        else:
            loggingFunctions().writeEvent(msg=f"{title} directory could not be found. Use default directory or specify correct location of {title} files to use this script.", msgType=failureAction)
            exit()
    loggingFunctions().writeEvent(msg=f'{title} Folder Verified:\t{Folder}')
    return

main()
