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

#Requires Python 3.x 
import csv, sys, argparse, collections
from datetime import datetime

#Argument Processing

helpMsg = '''
This script processes a CSV formated list of EPGs into XML files files used for creation.
'''

argsParse = argparse.ArgumentParser(description=helpMsg)
argsParse.add_argument('-i', '--input-file',  action='store', dest='inputFilePath',   required=True,                            help='File with CSV Data to be processed into ansible tasks')
argsParse.add_argument('-o', '--output-file', action='store', dest='outputDirectory', required=False, default='./sourceFolder', help='Destination File for XML Files')
args = argsParse.parse_args()

def writeTenant(tenant, outputFile, csvList):
    xmlFile = open(f'{outputFile}','w')
    xmlFile.write("<!-- dn=uni -->\n")
    xmlFile.write(f'<fvTenant name="{tenant}">\n')
    getVrfs(outputFile = outputFile, csvList = csvList, tenant = tenant)
        #TODO find and write each VRF in this tenate. 
            #TODO Look for and write RP if present in any entries
        #TODO find and write each BD in this tenant.
            #TODO Look for and write any Subnets associated with Bridge Domain
        #TODO Find and write each AP in this tenant.
            #TODO Find and write each EPG in this AP / Tenant combination.
    xmlFile.write(f'</fvTenant>\n')
    xmlFile.close()
    return

def getTenants(csvList, outputDirectory):
    #Find all of the VRFS for a specific tenant.
    fileTime = (datetime.now().strftime("%Y%m%d-%H%M%S"))
    tenant_list = []
    for line in csvList:
        if line['tenant'] not in tenant_list:
            tenant_list.append(line['tenant'])
    for tenant in tenant_list:
        #We only write one tenant to each file, because we don't want to hit the 64K limit for API requests.
        writeTenant(tenant = tenant, csvList = csvList, outputFile = f"{outputDirectory}/{fileTime}-{tenant}.xml")
    return

def getVrfs(csvList, outputFile, tenant):
    vrf_dict = {}
    count = 0
    for line in csvList:
        if (line['VRF'], line['tenant']) not in vrf_dict and line['tenant'] == tenant:
            print(f"tenant Name: {tenant}")
            print(f"VRF Name: {line['VRF']}")
            vrf_dict[(line['VRF'], line['tenant'])] = []
            count = count + 1
    print(count)
    print(vrf_dict)
    #writeVrfs(vrf_dict = vrf_dict, outputDirectory = outputDirectory)
    return


def writeVrfs(vrf_dict, outputDirectory):
    outputDirectory.write('vrfs:\n')
    for item in vrf_dict.items():
        (tenant, vrf), rp = item
        vrfFile = open(f'{outputDirectory}/{rowCount}-vrf.xml', 'w')
        vrfFile.write(f'<!-- dn=uni/tn-{tenant} -->')
        vrfFile.write
        outputDirectory.write(f" - vrf: {vrf}\n")
        outputDirectory.write(f"   tenant: {tenant}\n")

        if rp != 'NA':
            outputDirectory.write(f"   rp: {rp}\n")
        rowCount = rowCount + 1

def getApps(csvList, outputDirectory):
    app_dict = {}
    for line in csvList:
        if (line['tenant'], line['appProfile']) not in app_dict:
            app_dict[(line['tenant'],line['appProfile'])] = []
    writeApps(outputDirectory=outputDirectory, app_dict=app_dict)
    return

def writeApps(outputDirectory, app_dict):
    outputDirectory.write('aps:\n')
    for item in app_dict:
        (tenant, app) = item
        outputDirectory.write(f' - ap: {app}\n')
        outputDirectory.write(f'   tenant: {tenant}\n')
    return

def getBridgeDomains(outputDirectory, csvList):
    bd_dict = {}
    for line in csvList:
        if (line['tenant'], line['VRF'], line['bridgeDomain'], line['gateway'], line['mask'], line['l3Out']) not in bd_dict:
            bd_dict[(line['tenant'], line['VRF'], line['bridgeDomain'], line['gateway'], line['mask'], line['l3Out'])] = []
    writeBridgeDomains(outputDirectory = outputDirectory, bd_dict = bd_dict)
    return

def writeBridgeDomains(outputDirectory, bd_dict, scope='public'):
    outputDirectory.write('bridge_domains:\n')
    for item in bd_dict:
        (tenant, VRF, bridgeDomain, gateway, mask, l3Out) = item
        outputDirectory.write(f' - bd: {bridgeDomain}\n')
        outputDirectory.write(f'   gateway: {gateway}\n')
        outputDirectory.write(f'   mask: {mask}\n')
        outputDirectory.write(f'   tenant: {tenant}\n')
        outputDirectory.write(f'   vrf: {VRF}\n')
        outputDirectory.write(f'   scope: {scope}\n')
        outputDirectory.write(f'   L3Out: {l3Out}\n')
    return

def getEPGs(outputDirectory, csvList):
    epg_dict = {}
    for line in csvList:
        epg_dict[(line['tenant'],
            line['epgName'],
            line['bridgeDomain'],
            line['gateway'],
            line['mask'],
            line['description'],
            line['multiVRF'],
            line['domain'],
            line['domainType'],
            line['appProfile'],
            line['encap'],
            line['encapType'])] = []
    writeEPGs(outputDirectory = outputDirectory, epg_dict = epg_dict)
    return

def writeEPGs(outputDirectory, epg_dict):
    outputDirectory.write('epgs:\n')
    for item in epg_dict:
        (tenant, epgName, bridgeDomain, gateway, mask, description, multiVRF, domain, domainType, appProfile, encap, encapType) = item
        outputDirectory.write(f' - epg: {epgName}\n')
        outputDirectory.write(f'   tenant: {tenant}\n')
        outputDirectory.write(f'   ap: {appProfile}\n')
        outputDirectory.write(f'   bd: {bridgeDomain}\n')
        outputDirectory.write(f'   domain: {domain}\n')
        outputDirectory.write(f'   domainType: {domainType}\n')
        outputDirectory.write(f'   encaps: {encap}\n')
        outputDirectory.write(f'   encaptype: {encapType}\n')
        outputDirectory.write(f'   gateway: {gateway}\n')
        outputDirectory.write(f'   mask: {mask}\n')
        outputDirectory.write(f'   description: {description}\n')
        outputDirectory.write(f'   multivrf: {multiVRF}\n')
    return

def processCSV(outputDirectory):
    with open(f'{args.inputFilePath}', mode='r', encoding="utf-8-sig") as rawFile:
        #We open this as a list because we iterate it more than once
        csvContent = list(csv.DictReader(rawFile))

        #Generate Tenant List and write to outputDirectory
        getTenants(outputDirectory = outputDirectory, csvList = csvContent)

        #Generate VRF List and write to outputDirectory
        #getVrfs(outputDirectory = outputDirectory, csvList = csvContent)

        #Generate Application Profile List and write to outputDirectory
        #getApps(outputDirectory = outputDirectory, csvList = csvContent)
        
        #Generate Bridge Domain Profile List and write to outputDirectory
        #getBridgeDomains(outputDirectory = outputDirectory, csvList = csvContent)

        #Generate EPGs and write outputDirectory
        #getEPGs(outputDirectory = outputDirectory, csvList = csvContent)

rowCount = 1
processCSV(args.outputDirectory)
