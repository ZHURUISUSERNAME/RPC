"""
ShiPy RPC - 极简远程过程调用框架
===============================

特点:
- 轻量级: 核心代码不到 200 行
- 易用性: 简单易懂的 API
- 灵活性: 可以轻松扩展功能

作者: RuiZhu/Claude
日期: 2025-04-14
"""

import socket
import json
import pickle
import threading
import inspect
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ShiPy-RPC")

class RPCServer:
    """RPC 服务器，用于接收客户端请求并执行对应的函数"""
    
    def __init__(self, host="localhost", port=8888, max_connections=5):
        """
        初始化 RPC 服务器
        
        参数:
            host (str): 服务器主机名或 IP 地址
            port (int): 服务器端口号
            max_connections (int): 最大并发连接数
        """
        # 1. 租摊位(socket)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 2. 挂招牌(bind)
        self.socket.bind((host, port))
        # 设置最大连接数
        self.max_connections = max_connections
        # 注册的函数字典，键是函数名，值是函数对象
        self.functions = {}
        # 服务器是否运行的标志
        self.running = False
        
    def register_function(self, function):
        """
        注册一个函数，让它可以被远程调用
        
        参数:
            function: 要注册的函数对象
        """
        # 获取函数名
        func_name = function.__name__
        # 将函数保存到字典中
        self.functions[func_name] = function
        logger.info(f"注册函数: {func_name}{inspect.signature(function)}")
        
    def handle_client(self, client_socket, client_address):
        """
        处理客户端请求的线程函数
        
        参数:
            client_socket: 客户端套接字对象
            client_address: 客户端地址
        """
        print(f"服务端: 接收到客户端连接!")
        logger.info(f"客户端 {client_address} 已连接")
        
        try:
            while True:
                # 6. 收需求(recv)
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # 7. 解析需求
                try:
                    # 反序列化请求数据
                    request = pickle.loads(data)
                    func_name = request.get('function')
                    args = request.get('args', [])
                    kwargs = request.get('kwargs', {})
                    
                    # 查找并执行对应的函数
                    if func_name in self.functions:
                        function = self.functions[func_name]
                        result = function(*args, **kwargs)
                        # 构造成功响应
                        response = {
                            'status': 'success',
                            'result': result
                        }
                    else:
                        # 构造错误响应
                        response = {
                            'status': 'error',
                            'message': f"函数 '{func_name}' 未注册"
                        }
                        logger.warning(f"客户端请求未注册的函数: {func_name}")
                except Exception as e:
                    # 构造异常响应
                    response = {
                        'status': 'error',
                        'message': str(e)
                    }
                    logger.error(f"处理请求时出错: {e}")
                
                # 10. 打包响应
                serialized_response = pickle.dumps(response)
                
                # 11. 送货(send)
                client_socket.send(serialized_response)
        
        except ConnectionError:
            logger.info(f"客户端 {client_address} 断开连接")
        finally:
            # 12. 送客(close)
            client_socket.close()
            print(f"服务端: 客户端断开连接")
        
    def start(self):
        """启动 RPC 服务器，开始监听客户端请求"""
        if self.running:
            logger.warning("服务器已经在运行中")
            return
            
        self.running = True
        
        try:
            # 3. 开张听吆喝(listen)
            self.socket.listen(self.max_connections)
            
            # 4. while True:
            while self.running:
                try:
                    # 5. 等顾客(accept)
                    client_socket, client_address = self.socket.accept()
                    
                    # 创建新线程处理客户端请求
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except (KeyboardInterrupt, SystemExit):
                    break
                except Exception as e:
                    logger.error(f"接受客户端连接时出错: {e}")
                    
        finally:
            self.stop()
    
    def stop(self):
        """停止 RPC 服务器"""
        self.running = False
        self.socket.close()
        logger.info("RPC 服务器已停止")


class RPCClient:
    """RPC 客户端，用于调用远程服务器上的函数"""
    
    def __init__(self, host="localhost", port=8888):
        """
        初始化 RPC 客户端
        
        参数:
            host (str): 服务器主机名或 IP 地址
            port (int): 服务器端口号
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self):
        """连接到 RPC 服务器"""
        if self.connected:
            return
            
        try:
            # 创建套接字并连接到服务器
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"已连接到服务器 {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"连接服务器失败: {e}")
            raise ConnectionError(f"无法连接到服务器: {e}")
    
    def call(self, func_name, *args, **kwargs):
        """
        调用远程函数
        
        参数:
            func_name (str): 要调用的函数名
            *args: 位置参数
            **kwargs: 关键字参数
            
        返回:
            远程函数的返回值
        """
        if not self.connected:
            self.connect()
            
        # 构造请求
        request = {
            'function': func_name,
            'args': args,
            'kwargs': kwargs
        }
        
        # 序列化请求
        serialized_request = pickle.dumps(request)
        
        try:
            # 发送请求
            self.socket.send(serialized_request)
            
            # 接收响应
            response_data = self.socket.recv(4096)
            response = pickle.loads(response_data)
            
            # 处理响应
            if response.get('status') == 'success':
                return response.get('result')
            else:
                error_msg = response.get('message', '未知错误')
                raise Exception(f"RPC 调用失败: {error_msg}")
                
        except Exception as e:
            logger.error(f"RPC 调用出错: {e}")
            self.close()
            raise
    
    def close(self):
        """关闭与服务器的连接"""
        if self.connected and self.socket:
            self.socket.close()
            self.connected = False
            logger.info("已断开与服务器的连接")


# 以下是一个简单的使用示例

def example_server():
    """示例服务器"""
    def add(a, b):
        print(f"服务端: 正在计算 {a} + {b}")
        return a + b
        
    def hello(name):
        print(f"服务端: 有人在问候 {name}")
        return f"你好, {name}!"
        
    def get_time():
        return time.strftime("%Y-%m-%d %H:%M:%S")
        
    # 创建服务器并注册函数
    server = RPCServer("localhost", 8888)
    server.register_function(add)
    server.register_function(hello)
    server.register_function(get_time)
    
    print("RPC 服务器已启动，正在等待客户端连接...")
    server.start()

def example_client():
    """示例客户端"""
    # 创建客户端
    client = RPCClient("localhost", 8888)
    
    try:
        # 调用远程函数
        result1 = client.call("add", 5, 3)
        print(f"5 + 3 = {result1}")
        
        result2 = client.call("hello", "小明")
        print(result2)
        
        current_time = client.call("get_time")
        print(f"服务器时间: {current_time}")
    
    finally:
        # 关闭连接
        client.close()

if __name__ == "__main__":
    # 根据命令行参数决定运行服务器还是客户端
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        example_server()
    else:
        example_client()
