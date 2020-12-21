import requests as URL
# Disable warnings regarding certificates. 
URL.packages.urllib3.disable_warnings()

class urlFunctions:
    def __init__(self, args):
        self.apic = args.apic
        self.sourceFolder = args.sourceFolder
        self.writeScreen = loggingFunctions().writeScreen
        self.writeEvent = loggingFunctions().writeEvent
        return

    def getData(self, url, htmlMethod='GET',cookies='', data='', headers={"Content-Type": "application/xml"}):
        if htmlMethod == "POST":
            apiResponse = URL.post(url=url, data=f"{data}", headers=headers, verify=False, cookies=cookies)
        elif htmlMethod == "GET":
            apiResponse = URL.get(url=url, headers=headers, verify=False)
        return apiResponse

    def getCookie(self, user, password):
        self.writeScreen(msg='########## Starting Process to Get Cookie ##########')
        url = "https://{0}{1}".format(self.apic, "/api/aaaLogin.xml")
        self.writeEvent(msg = f"URL: {url}")
        logonRequest="<aaaUser name='{0}' pwd='{1}' />".format(user,password)
        getCookieResponse = self.getData(url=url, htmlMethod="POST", data=logonRequest)
        self.httpErrorReporting(status=getCookieResponse.status_code, reason=getCookieResponse.reason)
        return getCookieResponse
    
    def httpErrorReporting(self, status, reason='', msgType='FAIL'):
        if status in range(200, 299):
            self.writeEvent(msg=f'API Access Completed Successfully')
        elif status in range(400, 599):
            self.writeEvent(msg=f'API Access Failed\tReason: {reason}',msgType=msgType)
            self.writeEvent(msg='Script will exit',msgType=msgType)
        return

class loggingFunctions:
    def __init__(self):
        return
    
    def writeEvent(self, msg, msgType='INFO'):
        self.writeScreen(msg, msgType)
        return
    
    def writeLog(self):
        return

    def writeScreen(self, msg, msgType='INFO'):
        if msgType == 'INFO':
            print(f"[ {textColors.INFO}INFO{textColors.noColor} ] {msg}")
        elif msgType == 'WARN':
            print(f"[ {textColors.WARN}WARN{textColors.noColor} ] {msg}")
        elif msgType == "FAIL":
            print(f"[ {textColors.FAIL}FAIL{textColors.noColor} ] {msg}")
        else:
            print(f"[ {textColors.FAIL}UNKNOWN{textColors.noColor} ] {msg}")
            print(f"This is a developer bug. Script will exit")
            exit()
        return

# Colors used in text output that can be called by name. 
class textColors:
        noColor = '\x1b[0m'
        INFO = '\033[32m'
        WARN = '\033[33m'
        FAIL = '\033[31m'
