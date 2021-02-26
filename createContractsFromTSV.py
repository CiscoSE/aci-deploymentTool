__license__ = """
Copyright (c) 2021 Cisco and/or its affiliates.

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
import csv, sys, argparse, collections, re
from datetime import datetime

#Argument Processing

helpMsg = '''
This script processes a Tab Seperated Value file of Contracts to be created based on existing filters.
'''

argsParse = argparse.ArgumentParser(description=helpMsg)
argsParse.add_argument('-i', '--input-file',  action='store', dest='inputFilePath',   required=True,                            help='File with CSV Data to be processed into ansible tasks')
argsParse.add_argument('-o', '--output-file', action='store', dest='outputDirectory', required=False, default='./sourceFolder', help='Destination File for XML Files')
args = argsParse.parse_args()

class loggingFunctions:
    noColor = '\x1b[0m'
    INFO = '\033[32m'
    WARN = '\033[33m'
    FAIL = '\033[31m'
    
    def __init__(self):
        return

    def writeScreen(self, msg, msgType='INFO', exitOnFail = False):
        if msgType == 'INFO':
            print(f"[ {self.INFO}INFO{self.noColor} ] {msg}")
        elif msgType == 'WARN':
            print(f"[ {self.WARN}WARN{self.noColor} ] {msg}")
        elif msgType == "FAIL":
            print(f"[ {self.FAIL}FAIL{self.noColor} ] {msg}")
            if exitOnFail == True: exit()
        else:
            print(f"[ {self.FAIL}UNKNOWN{self.noColor} ] {msg}")
            print(f"This is a developer bug. Script will exit")
            exit()
        return

class tsvProcessing:
    def __init__(self, args):
        self.inputFilePath = args.inputFilePath
        self.outputDirectory = args.outputDirectory
        return

    def main(self):
        with open(f'{args.inputFilePath}', mode='r', encoding="utf-8-sig") as rawFile:
            #We open this as a list because we iterate it more than once
            self.tsvList = list(csv.DictReader(rawFile, delimiter='\t'))

            #Generate Tenant List and write to outputDirectory
            self.getTenants()
        return
    
    def getTenants(self):
        #Find all of the VRFS for a specific tenant.
        fileTime = (datetime.now().strftime("%Y%m%d-%H%M%S"))
        tenant_list = []
        for line in self.tsvList:
            if line['tenant'] not in tenant_list:
                tenant_list.append(line['tenant'])
        for tenant in tenant_list:
            #We only write one tenant to each file, because we don't want to hit the 64K limit for API requests.
            self.writeTenant(tenant = tenant, outputFile = f"{self.outputDirectory}/{fileTime}-{tenant}.xml")
        return
    
    def writeTenant(self, tenant, outputFile):
        loggingFunctions().writeScreen(f'Opening file:\t{outputFile}')
        xmlFile = open(f'{outputFile}','w')
        loggingFunctions().writeScreen(f'Writing Tenant entries for Tenant: {tenant}')
        #We need this for the deployment script, but we make it as comment so we can ignore it if pushing via curl or similar method.
        xmlFile.write(f"<!-- dn=uni/tn-{tenant} -->\n")
        xmlFile.write(f'<!-- Creating Tenant reference place holder, which allows for multiple contracts in the same file -->\n')
        #Because the DN points to the tenant, we don't need the tenant name or DN in the tenant object itself. 
        #We add this so we can do multiple contracts under a single tenant. 
        xmlFile.write(f'<fvTenant>\n')
        self.getContracts(tenant=tenant, xmlFile=xmlFile)
        xmlFile.write(f'</fvTenant>\n')
        loggingFunctions().writeScreen(f'Closing Tenant File:\t {outputFile}')
        xmlFile.close()
        return

    def getContracts(self, tenant, xmlFile):
        contract_list = []
        for line in self.tsvList:
            if line['tenant'] == tenant and line['contractName'] not in contract_list:
                contract_list.append(line['contractName'])
        self.writeContracts(contract_list=contract_list, tenant=tenant, xmlFile=xmlFile)
        return
    
    def returnScope(self, tenant, contract):
        scopeList = []
        for line in self.tsvList:
            if line['tenant'] == tenant and line['contractName'] == contract and line['contractScope'] not in scopeList:
                scopeList.append((line['contractScope']).lower())

        if 'global' in scopeList:
            return 'global'
        elif 'tenant' in scopeList:
            return 'tenant'
        elif 'vrf' in scopeList or 'context' in scopeList:
            return 'context'
        elif 'application-profile' in scopeList:
            return 'application-profile'

        # If we cannot figure it out, we return global
        loggingFunctions().writeScreen(f'Unable to determine scope for contract {contract} in tenant {tenant}.', 'WARN')
        loggingFunctions().writeScreen('Setting scope to global', 'WARN')

        return 'global'
    
    def writeContracts(self, contract_list, tenant, xmlFile):
        for contract in contract_list:
            contractScope = self.returnScope(tenant=tenant, contract=contract)
            xmlFile.write(f'\t<!-- This is the name of the contract -->\n')
            xmlFile.write(f'\t<vzBrCP intent="install" name="{contract}" scope="{contractScope}" >\n')
            self.getSubjects(contract=contract,tenant=tenant,xmlFile=xmlFile)
            xmlFile.write(f'\t</vzBrCP>\n')
        return

    def getSubjects(self, contract, tenant, xmlFile):
        subject_dict = {}
        for line in self.tsvList:
            if line['tenant'] == tenant and line['contractName'] == contract and line['contractSubject'] not in subject_dict:
                subject_dict[(line['contractSubject'])] = line['reversed']
        for subject in subject_dict.items():
            self.writeSubject(tenant=tenant, contract=contract, subject=subject, xmlFile=xmlFile)
        return
    
    
    def writeSubject(self, tenant, contract, subject, xmlFile):
        (subjectName), reversedPort = subject
        if reversedPort == False or reversedPort.lower() == "no":
            reversedPortValue = "no"
        else:
            reversedPortValue = "yes"
        xmlFile.write(f'\t\t<!-- This is the subject under contract {contract} -->\n')
        xmlFile.write(f'\t\t<vzSubj name="{subjectName}" consMatchT="AtleastOne" provMatchT="AtleastOne" revFltPorts="{reversedPortValue}" >\n')
        self.getFilters(tenant=tenant, contract=contract, subject=subjectName, xmlFile=xmlFile)
        xmlFile.write(f'\t\t</vzSubj> \n')
        return
    
    def getFilters(self, tenant, contract, subject, xmlFile):
        filter_list = []
        for line in self.tsvList:
            if line['tenant'] == tenant and line['contractName'] == contract and line['contractSubject'] == subject and line['subjectFilters'] not in filter_list:
                if ',' in line['subjectFilters']:
                    filters_list = (line['subjectFilters']).split(',')
                    for filter in filters_list:
                        if filter.strip() not in filter_list:
                            filter_list.append(filter.strip())
                            self.writeFilter(filter=filter, xmlFile=xmlFile)
                else:
                    filter_list.append(line['subjectFilters'])
                    self.writeFilter(filter=filter, xmlFile=xmlFile)

        return

    def writeFilter(self, filter, xmlFile):
        xmlFile.write(f'\t\t\t<!-- These are the filters for allowed protocols --> \n')
        xmlFile.write(f'\t\t\t<vzRsSubjFiltAtt action="permit" tnVzFilterName="{filter}" />\n')
        return
tsvProcessing(args).main()

