from shipy_rpc import RPCClient

# 创建客户端
client = RPCClient("localhost", 8888)

# 调用远程函数
area = client.call("calculate_area", 10, 5)
print(f"面积是: {area}")

# 关闭连接
client.close()

