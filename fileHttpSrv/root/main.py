# !E:\python\venv\Scripts\
# -*- coding:utf-8 -*-

# 全局变量
SESSION = None
POST = None
rawPOST= None
GET = None


def app():
    if POST is not None:
        print('POST ', POST)
        if ('name' in POST.keys()) and ('password' in POST.keys()) and (POST['name'] == 'abc') and (POST['password']=='123'):
            SESSION.setCookie('name', 'abc')
            SESSION.write2XML()
            return 'login success!'
        else:
            with open('root/login.html', 'r') as f:
                data = f.read()
                data = data.replace('<form', '失败！Wrong name or password!<form')
            return data
    else:
        if SESSION.getCookie('name') is not None:
            return 'hello, '+SESSION.getCookie('name') + '! 我认识你'
        with open('root/login.html', 'r') as f:
            data = f.read()
            data = data.replace('<form', '请登陆！No Cookie found!<form')
        return data