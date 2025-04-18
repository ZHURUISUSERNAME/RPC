from shipy_rpc import RPCServer

# 定义要暴露的函数
def calculate_area(length, width):
    return length * width

# 创建服务器并注册函数
server = RPCServer("localhost", 8888)
server.register_function(calculate_area)

# 启动服务器
print("服务器已启动...")
server.start()

