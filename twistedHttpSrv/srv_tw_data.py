#coding:utf-8

from twisted.web.resource import Resource
from twisted.web import server
from twisted.internet import reactor, endpoints
from urllib import parse

import json

def myFunc1(a, b):
    return a+b
    
def decode_args(args):
    args_2 = dict()
    for key in args:
        key_2 = key.decode('utf-8')
        l = args[key]
        l_2 = []
        for i in l:
            l_2.append(i.decode('utf-8'))
        args_2[key_2] = (l_2)
    return args_2
class Server(Resource):
    isLeaf = True

    def getChild(self, path, request):
        if path == '':
            return self
        return Resource.getChild(self, path, request)

    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/json')   # text/json居然默认不是utf-8
        request.setHeader('Access-Control-Allow-Origin', '*')    # 允许被跨域调用
        
        args = decode_args(request.args)    # url中的参数保存在 request.args 中
        path = str(request.path, 'utf-8')        # 路径 request.path= b'/this/is'

        msg = 'GET调用结果。。'
        if(path == '/func' or path=='/func1/'):
            msg = myFunc1(2,3)
            
        res = {'method':'GET', 'path':path, 'args':args}
        res['out'] = msg
        retstr = json.dumps(res, ensure_ascii=False)  #..,encoding="UTF-8", ensure_ascii=False)
        return retstr.encode('utf-8')        # 返回值应当是一个字节流

    def render_POST(self, request):
        request.setHeader('Content-Type', 'application/json')   # text/json居然默认不是utf-8
        request.setHeader('Access-Control-Allow-Origin', '*')    # 允许被跨域调用

        args = decode_args(request.args)    # url中的参数保存在 request.args 中，post的符合表单格式的k=v对也在args中。
        path = str(request.path, 'utf-8')        # 路径 request.path= b'/this/is'
        data = request.content.getvalue().decode('utf-8')

        msg = 'POST处理结果'
        if(path == '/func' or path=='/func1/'):
            msg = myFunc1(2,3)
        #print('POST...path=', path)    # path= b'/this/is'  if post to url 'http://127.0.0.1:12347/this/is?a=1&b=2'
        #print('arg=', args)      # arg= {'a': ['de中啊文fg'], 'd': ['20190722']}
        #print('post data:', data)
        res = {'method':'POST', 'path':path, 'args':args, 'data': data, 'out': msg}
        res['dec_data'] = parse.unquote(data)
        retstr = json.dumps(res, ensure_ascii=False)
        return retstr.encode('utf-8')

if __name__ == '__main__':

    # 监听的端口号
    port = 9606

    site = server.Site(Server())
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(site)
    print('READY at port ', port)
    reactor.run()