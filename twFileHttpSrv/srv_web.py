#coding:utf-8
from twisted.web.resource import Resource
from twisted.web import server
from twisted.internet import reactor, endpoints

import os, sys, json, re
from urllib import parse

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
    
cntypDict = {
    'htm':'text/html', 'html':'text/html',
    'css':'text/css',
    'js' :'application/x-javascript',
    'png':'image/png', 
    'gif':'image/gif', 
    'tif':'image/tiff', 'tiff':'image/tiff', 
    'jpg':'image/jpeg', 'jpeg':'image/jpeg', 'jpe':'image/jpeg', 
    'mp3':'audio/mp3',
    'mp4':'video/mpeg4','mpeg':'video/mpg','mpg':'video/mpg',
    'mpa':'video/x-mpg','mps':'video/x-mpeg',
    'mpe':'video/x-mpeg','mpga':'audio/rn-mpeg',
    'swf':'application/x-shockwave-flash'    
}
def contentType(fp):
    pp = fp.rfind('.')
    ext = fp[pp+1:]
    
    if(ext in cntypDict.keys()):
        return(cntypDict[ext])
        
    return('application/octet-stream')

def redirect(fp):
    return('<!DOCTYPE html><html><script>window.location = "'+fp+'";</script></html>')

fileRoot = './web'      # 文件服务的根目录

class Server(Resource):
    isLeaf = True

    def getChild(self, path, request):
        if path == '':
            return self
        return Resource.getChild(self, path, request)

    def render_GET(self, request):
        args = decode_args(request.args)    # url中的参数保存在 request.args 中
        path = str(request.path, 'utf-8')        # 路径 request.path= '/this/is'
        
        fp = fileRoot + path
        if(fp[-1]=='/'):
            fp += 'index.html'
            
        bFileExsist = False
        
        if(os.path.exists(fp)):
            if(not os.path.isfile(fp)):        # 存在但是是目录
                nfp = fp + '/index.html'
                if(os.path.exists(nfp) and os.path.isfile(nfp)):    # 目录下有index.html
                    request.setHeader('Content-Type', 'text/html')
                    return(redirect(fp+'/').encode('utf-8'))  # 末尾不带/，跳转到加/的地址，以免页面内相对链接缺少一层目录
                else:
                    bFileExsist = False
            else:
                bFileExsist = True            # 存在且是文件
                
        if(bFileExsist):
            ctyp = contentType(fp)
            print('GET ... 读file: path=', path, 'as: ', ctyp)

            fr = open(fp, 'rb')     # 文本类型，也这样读写，省去.encode('utf8')
            res = fr.read()
            fr.close()
            request.setHeader('Content-Type', ctyp)
            
            return res
        else:
            msg = 'Oops! 找不到这个文件: ' + fp
            if(path == '/func' or path=='/func1/'):
                msg = myFunc1(2,3)
            #print('GET ... file不存在: path=', path)
            request.setHeader('Content-Type', 'application/json')   # 默认utf-8
            request.setHeader('Access-Control-Allow-Origin', '*')    # 允许跨域调用
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
    port = 9601

    site = server.Site(Server())
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(site)
    print('READY at port ', port)
    reactor.run()
