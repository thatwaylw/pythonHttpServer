# -*- coding=utf-8 -*-
import socket, threading, queue
from urllib import parse
import json

host = '0.0.0.0'
port = 9619

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
        (key, val) = (tok[0], tok[1]) if(len(tok)>1) else (tok[0], '')
        if(key):    key = parse.unquote(key)
        if(val):    val = parse.unquote(val)
        d[key] = val
    return d

class HttpRequest(object):          # 核心类，处理Request，生成Response
    def __init__(self):
        self.method = None
        self.url = None
        self.protocol = None
        self.head = dict()
        self.request_param = dict()     # url参数，不管GET还是POST
        self.request_postdata = None    # post的data，不一定是 a=1&d=2的形式
        self.request_postdic = dict()   # post的data，如果是 a=1&d=2的形式
        self.response_line = ''
        self.response_head = dict()
        self.response_body = ''

    def passRequestLine(self, request_line):
        header_list = request_line.split(' ')
        self.method = header_list[0].upper()
        self.url = header_list[1]
        self.protocol = header_list[2]

    def passRequestHead(self, request_head):
        head_options = request_head.split('\r\n')
        for option in head_options:
            key, val = option.split(': ', 1)
            self.head[key] = val
            # print key, val

    def passRequest(self, request):
        request = request.decode('utf-8')
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
            self.dynamicRequest(s_url)
        else:                               # ...url不带参数，的GET或者POST
            self.dynamicRequest(self.url)

    def dynamicRequest(self, path):
        #print('*** dynamic Request *** path=', path)
        self.response_line = ErrorCode.OK
        
        res_json = {'method': self.method, 'args': self.request_param, 'path': path}
        res_json['data_param'] = self.request_postdic
        res_json['data'] = self.request_postdata
        #if(self.request_postdata):     # 好像json.dump会自动unquote解码。？
        #    res_json['dec_data'] = parse.unquote(self.request_postdata)
        res_json['out'] = myFunc1(2,3)
        
        self.response_body = json.dumps(res_json, ensure_ascii=False)
            
        self.response_head['Content-Type'] = 'application/json' #默认utf8,可以中文
        self.response_head['Access-Control-Allow-Origin'] = '*' #数据接口，允许跨域访问，可以被ajax调用

    def getResponse(self):
        resp = self.response_line + dict2str(self.response_head) + '\r\n'
        resp += self.response_body
        resp = resp.encode('utf-8')
        return resp

def myFunc1(a, b):
    return a+b

# 每个任务线程
class WorkThread(threading.Thread):
    def __init__(self, work_queue):
        super().__init__()
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        while True:
            func, args = self.work_queue.get()
            func(*args)
            self.work_queue.task_done()

# 线程池
class ThreadPoolManger():
    def __init__(self, thread_number):
        self.thread_number = thread_number
        self.work_queue = queue.Queue()
        for i in range(self.thread_number):     # 生成一些线程来执行任务
            thread = WorkThread(self.work_queue)
            thread.start()

    def add_work(self, func, *args):
        self.work_queue.put((func, args))

def tcp_link(sock, addr):
    #print('Accept new connection from %s:%s...' % addr)
    request = sock.recv(1024)
    http_req = HttpRequest()
    http_req.passRequest(request)
    sock.send(http_req.getResponse())
    sock.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(10)
    thread_pool = ThreadPoolManger(5)
    print('listen in %s:%d' % (host, port))
    while True:
        sock, addr = s.accept()
        thread_pool.add_work(tcp_link, *(sock, addr))


if __name__ == '__main__':
    start_server()
    pass

