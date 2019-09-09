# pythonHttpServer
用python部署http服务，以及web文件服务

dataHttpSrv - 最简单的数据接口，能处理GET和POST请求，返回json格式数据，支持ajax跨域调用

fileHttpSrv - 加入简单的文件web服务，支持常见的图片，js，css外部文件

twistedHttpSrv - 用Tiwsted库实现的Http服务器
// 安装说明：
	pip install service_identity
    pip install twisted

// 启动方法：
	简单启动：python3 srv_data.py
	常驻启动：nohup python3 srv_data.py &
