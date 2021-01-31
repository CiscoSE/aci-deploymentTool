# Files
Two files for bulk loading EPGs into tenants.

- createXMLfromTSV.py - Creates XML for EPGs for deployment from a tab seperated value file.
- deployACIChanges.py - Deployes XML to ACI 

# Supporting Files
- bin/common.py - Support file for deployACIChanges.py
- tabSeperatedValue-examples\examples-Tenants.v2.txt - an Example file to show required fields, and example data

# Requirements:
Tested on python3 version 3.7.2

Must have python requests for deployACIChanges.py

> pip3 install requests

# Required Folders
When running deployACIChanges.py we require a source and processed folder. 

- processedFolder - The processed files directory is where processed XML is moved to after sending the XML to the APIC This provides a history of files processed. File is is moved, and no effort is made to protect over writting existing files.
-- You can specify the processed folder as an argument using the processedFolder arugment
- sourceFolder - the sourceFolder is searched for .xml files. All XML files will be processed if placed in this folder.

# Using createXMLfromTSV.py to generate XML
You need to fill out a tab seperated value file with one line for each EPG. The example file provided shows fields and various data entry options.

The following fields are required:
- bridgeDomain
- tenant - The name of the Tenent to be created
- VRF - The name of the VRF to be created.
- vrfEnforced - Specifies whether a VRF is enforced or not
-- Must be TRUE or FALSE
- appProfile - the name of the Application Profile to be created under the tenant. 
- egpName - The name of the EPG to be created under the appProfile and tenant.
- domain - Only one domain can be added per EPG with this script at this time. 
- domainType - The type of domain being added
-- phys or vmm are the only supported domain types at this time.
- encap - the VLAN number to be assigned to the domain for domain assignments.
Optional fields:
- description - The description for the EPG
- multiVRF - When set to YES, routes from bridge domain subnet can be shared with other VRFs. If set to anything else, bridge domain subnet will not be shared with other VRFs.

Future Options:
Still working on L3Out and rrendezvous points (RP). These field will be implemented in future revisions. Additional support for contract mapping to existing contracts is also planned.

Command line example - Run createXMLfromTSV.py with python3 with the example txt file as a source, and tenant output files written to the source folder in the same directory:

`python3 ./createXMLfromTSV.py -i ./tabSeperatedValue-examples/example-Tenants.v2.txt -o ./sourceFolder`

# Deploying generated XML files to an APIC
This script does zero error checking. If you have a properly formatted your xml file, and specify an accessible APIC, the file will be deploy with no error checking and no respect for what is on the APIC.

<span style="color:red">THIS FILE CAN HURT YOUR SYSTEM IF YOU DO NOT UNDERSTAND HOW IT WORKS - YOU SHOULD UNDERSTAND BASIC APIC API DEPLOYMENT AND TEST ON NON_PRODUCTION SYSTEMS BEFORE USING IT!</span>
<span style=""color:red">DO A BACKUP BEFORE YOU RUN THIS!"</span>
This script requires a fail safe switch to run to ensure you mean to make changes. The script will not run without the --fail-safe switch. 

The first line of any XML file must be a comment line with the dn in it. As on of now, we only support the following entry, but others are expected in the future

`<!-- dn=uni -->`

If you are using the default sourceFolder, you only need to specify the user name and APIC IP along with the fail safe switch to run the script. Files will be read from the source folder and moved to the processedFolder:

`python3 ./deployACIChanges.py -u admin -a 172.16.1.11 --fail-safe`



