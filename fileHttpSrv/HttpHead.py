# -*- coding:utf-8 -*-
import os
import xml.dom.minidom


# 返回码
class ErrorCode(object):
    OK = "HTTP/1.1 200 OK\r\n"
    NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"


# 将字典转成字符串
def dict2str(d):
    s = ''
    for k, v in d.items():
        #if(v==None): v = ''
        if(v==None): continue
        s = s + k + ': ' + v + '\r\n'
    return s
    
# 将k=v&k=v形式的数据转成字典，GET POST皆有可能，可能缺失=等等
def param2dict(s):
    d = {}
    parameters = s.split('&')
    for i in parameters:
        tok = i.split('=', 1)
        #key, val = tok if(len(tok)>1) else (tok[0], None)  #这样写也行
        (key, val) = (tok[0], tok[1]) if(len(tok)>1) else (tok[0], '')
        d[key] = val
    return d

class Session(object):
    def __init__(self):
        self.data = dict()
        self.cook_file = None

    def getCookie(self, key):
        if key in self.data.keys():
            return self.data[key]
        return None

    def setCookie(self, key, value):
        self.data[key] = value

    def loadFromXML(self):
        import xml.dom.minidom as minidom
        print(' %%% Load Cookie from: ', self.cook_file)
        root = minidom.parse(self.cook_file).documentElement
        for node in root.childNodes:
            if node.nodeName == '#text':
                continue
            else:
                self.setCookie(node.nodeName, node.childNodes[0].nodeValue)        

    def write2XML(self):
        import xml.dom.minidom as minidom
        dom = xml.dom.minidom.getDOMImplementation().createDocument(None, 'Root', None)
        root = dom.documentElement
        for key in self.data:
            node = dom.createElement(key)
            node.appendChild(dom.createTextNode(self.data[key]))
            root.appendChild(node)
        print(' %%% write Cookie to: ', self.cook_file)
        with open(self.cook_file, 'w') as f:
            dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')


class HttpRequest(object):
    RootDir = 'root'
    NotFoundHtml = RootDir+'/404.html'
    CookieDir = 'root/cookie/'

    def __init__(self):
        self.method = None
        self.url = None
        self.protocol = None
        self.head = dict()
        self.Cookie = None
        self.request_param = dict()     # url参数，不管GET还是POST
        self.request_postdata = None    # post的data，不一定是 a=1&d=2的形式
        self.request_postdic = dict()   # post的data，如果是 a=1&d=2的形式
        self.response_line = ''
        self.response_head = dict()
        self.response_body = ''
        self.session = None

    def passRequestLine(self, request_line):
        header_list = request_line.split(' ')
        self.method = header_list[0].upper()
        self.url = header_list[1]
        if self.url == '/':
            self.url = '/index.html'
        self.protocol = header_list[2]

    def passRequestHead(self, request_head):
        head_options = request_head.split('\r\n')
        for option in head_options:
            key, val = option.split(': ', 1)
            self.head[key] = val
            # print key, val
        if 'Cookie' in self.head:
            self.Cookie = self.head['Cookie']

    def passRequest(self, request):
        request = request.decode('utf-8')
        print('>>>>>>>>> request >>>>>>>>>>>>>>>')
        print(request)
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        if len(request.split('\r\n', 1)) != 2:
            return
        request_line, body = request.split('\r\n', 1)
        request_head = body.split('\r\n\r\n', 1)[0]     # 头部信息
        self.passRequestLine(request_line)
        self.passRequestHead(request_head)

        if self.method == 'POST':                  # 处理POST data；如果有
            request_body = body.split('\r\n\r\n', 1)[1]
            self.request_postdata = request_body
            self.request_postdic = param2dict(request_body)

        if self.url.find('?') != -1:        # ...如果是含有参数的GET，或者POST
            req = self.url.split('?', 1)[1]
            s_url = self.url.split('?', 1)[0]  # 去除参数之后的文件名
            self.request_param = param2dict(req)
            self.dynamicRequest(HttpRequest.RootDir + s_url)
        # 所有post视为动态请求
        # get如果带参数也视为动态请求
        # 不带参数的get视为静态请求
        else:                               # ...url不带参数，的GET或者POST
            if self.method == 'POST':
                self.dynamicRequest(HttpRequest.RootDir + self.url)
            else:
                self.staticRequest(HttpRequest.RootDir + self.url)

    # 只提供制定类型的静态文件
    def staticRequest(self, path):
        #print('*** static Request *** path=', path)
        if not os.path.isfile(path):
            f = open(HttpRequest.NotFoundHtml, 'r')
            self.response_line = ErrorCode.NOT_FOUND
            self.response_head['Content-Type'] = 'text/html'
            self.response_body = f.read()
        else:
            extension_name = os.path.splitext(path)[1]  # 扩展名
            ext_ConTyp = {'.css':'text/css', '.html':'text/html', '.js':'application/x-javascript'}
            img_ConTyp = {'.png':'image/png', 
                          '.gif':'image/gif', 
                          '.tif':'image/tiff', '.tiff':'image/tiff', 
                          '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.jpe':'image/jpeg'}
            if extension_name in img_ConTyp:
                f = open(path, 'rb')
                self.response_line = ErrorCode.OK
                self.response_head['Content-Type'] = img_ConTyp[extension_name]
                self.response_body = f.read()        # 就这里特殊，是bytes。。还不能转str
            elif extension_name in ext_ConTyp:
                f = open(path, 'r')
                self.response_line = ErrorCode.OK
                self.response_head['Content-Type'] = ext_ConTyp[extension_name]
                self.response_body = f.read()
            elif extension_name == '.py':
                self.dynamicRequest(path)
            # 其他文件不返回
            else:
                f = open(HttpRequest.NotFoundHtml, 'r')
                self.response_line = ErrorCode.NOT_FOUND
                self.response_head['Content-Type'] = 'text/html'
                self.response_body = f.read()

    def processSession(self):
        self.session = Session()
        # 没有提交cookie，创建cookie
        if self.Cookie is None:
            print(' %%% Cookie is None, create one')
            self.Cookie = self.generateCookie()
            cookie_file = self.CookieDir + self.Cookie
            self.session.cook_file = cookie_file
            self.session.write2XML()
        else:            
            cookie_file = self.CookieDir + self.Cookie
            self.session.cook_file = cookie_file
            if os.path.exists(cookie_file):
                self.session.loadFromXML()                
            # 当前cookie不存在，自动创建
            else:
                print(' %%% Cookie file name wrong, create new one')
                self.Cookie = self.generateCookie()
                cookie_file = self.CookieDir+self.Cookie
                self.session.cook_file = cookie_file
                self.session.write2XML()                
        return self.session


    def generateCookie(self):
        import time, hashlib
        cookie = str(int(round(time.time() * 1000)))
        hl = hashlib.md5()
        hl.update(cookie.encode(encoding='utf-8'))
        return cookie

    def dynamicRequest(self, path):
        #print('*** dynamic Request *** path=', path)
        # 如果找不到或者后缀名不是py则输出404
        if not os.path.isfile(path) or os.path.splitext(path)[1] != '.py':
            f = open(HttpRequest.NotFoundHtml, 'r')
            self.response_line = ErrorCode.NOT_FOUND
            self.response_head['Content-Type'] = 'text/html'
            self.response_body = f.read()
        else:
            # 获取文件名，并且将/替换成. import subfolder.module
            file_path = path.split('.', 1)[0].replace('/', '.')
            print('~~~~~~ call Python: ', file_path)
            self.response_line = ErrorCode.OK

            m = __import__(file_path)
            
            if('main.py' in path):
                m.main.SESSION = self.processSession()            
                if self.method == 'POST':
                    m.main.rawPOST = self.request_postdata
                    m.main.POST = self.request_postdic
                    m.main.GET = self.request_param
                else:
                    m.main.POST = None
                    m.main.GET = self.request_param
                self.response_body = m.main.app()            
            elif('func1.py' in path):
                if self.method == 'POST':
                    m.func1.GET = self.request_param
                    m.func1.rawPOST = self.request_postdata
                    m.func1.POST = self.request_postdic
                else:
                    m.func1.GET = self.request_param
                self.response_body = m.func1.app()            
            
            self.response_head['Content-Type'] = 'text/html; charset=UTF-8' #这样函数返回字符串可以中文
            self.response_head['Set-Cookie'] = self.Cookie
            self.response_head['Access-Control-Allow-Origin'] = '*'

    def getResponse(self):
        print('<<<<<<<<<<<<<< response <<<<<<<<<<<<<<<<')
        resp = self.response_line + dict2str(self.response_head)+'\r\n'
        if(type(self.response_body)==str):
            resp += self.response_body
            print(resp)
            resp = resp.encode('utf-8')
        else: # body 是图片等二进制数据，无需encode
            print(resp + '@@ Binary data .. @@')
            resp = resp.encode('utf-8')
            resp += self.response_body
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        return resp
