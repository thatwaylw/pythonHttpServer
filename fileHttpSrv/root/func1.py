# -*- coding:utf-8 -*-
from urllib import parse
# 全局变量
SESSION = None
POST = None
rawPOST= None
GET = None

def app():

    print('GET=', GET)
    if(GET):
        for k,v in GET.items():
            print('%s=%s' % (k, parse.unquote(v)), end='; ')
        print('')
    print('POST=', POST)
    if(POST):
        for k,v in POST.items():
            print('%s=%s' % (k, parse.unquote(v)), end='; ')
        print('')
    print('rawPOST=', rawPOST)
    
    return 'Result from func1.py！哈哈~~'
    