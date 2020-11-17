import sys
import os
import argparse
import getpass



#Append path for files in the bin directory
sys.path.append(os.getcwd() + '/bin')

#Import URL functions from the common.py file. We use these for all API communication
from common import urlFunctions

#clear the terminal window before we continue
os.system('clear')

#########################
# Argument Handling
#########################

helpMsg = """
Deployment Tool for pushing XML configuration files for Cisco ACI APICs. 
"""

argsParse = argparse.ArgumentParser(description=helpMsg)
argsParse.add_argument('-s', '--server',         action='store', dest='server',       default='10.82.66.223', help='APIC IP addresses or FQDN to be changed.' )
argsParse.add_argument('-u', '--user',           action='store', dest='user',         default='admin',        help='User name for APIC Access' )
argsParse.add_argument('-p', '--password',       action='store', dest='password',     default='somePassword', help='Password for APIC Access' )
argsParse.add_argument('-f', '--source-folder',  action='store', dest='sourceFolder', default='somePassword', help='Password for APIC Access' )

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
    print(args)
main()