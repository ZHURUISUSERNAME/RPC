# 文件名: server_node.py
from concurrent import futures
import logging
import time
import grpc
import json
import os
import greeter_pb2
import greeter_pb2_grpc
import signal
import argparse # 导入 argparse 用于解析命令行参数
import sys     # 用于 sys.exit

# 使用绝对路径存储数据文件，文件名包含端口号
# DATA_FILE = os.path.join(os.path.dirname(__file__), "kv_store.json") # 旧方式
DATA_FILE_TEMPLATE = os.path.join(os.path.dirname(__file__), "kv_store_{}.json") # 新模板

class KeyValueStore(greeter_pb2_grpc.KeyValueStoreServicer):
    # 修改构造函数以接收节点信息
    def __init__(self, port, peers_addr):
        self.port = port # 存储自己的端口
        self.store = {}
        self.data_file = DATA_FILE_TEMPLATE.format(port) # 根据端口生成数据文件名
        self.peers = {} # 存储对等节点的 gRPC 存根 (stubs)
        self.peers_addr = peers_addr # 存储对等节点的地址字符串列表

        self._load_data()
        self._connect_to_peers() # 初始化时连接到对等节点

    def _connect_to_peers(self):
        """根据提供的地址列表，创建到其他节点的 gRPC 连接和存根"""
        logging.info(f"[Node {self.port}] 尝试连接到对等节点: {self.peers_addr}")
        for addr in self.peers_addr:
            if not addr: continue # 跳过空地址
            try:
                # 创建到对等节点的非安全通道
                channel = grpc.insecure_channel(addr)
                # 注意：这里可以添加等待通道就绪的逻辑，但为简单起见省略
                # grpc.channel_ready_future(channel).result(timeout=5) # 例如等待5秒
                stub = greeter_pb2_grpc.KeyValueStoreStub(channel)
                self.peers[addr] = stub
                logging.info(f"[Node {self.port}] 成功连接到对等节点: {addr}")
            except Exception as e:
                # 在这个简单版本中，连接失败我们只记录日志
                logging.error(f"[Node {self.port}] 连接到对等节点 {addr} 失败: {e}")
                # 可以在这里添加重试逻辑，但目前省略

    def _load_data(self):
        """加载持久化的键值数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.store = json.load(f)
                logging.info(f"[Node {self.port}] 成功从 {self.data_file} 加载了 {len(self.store)} 条数据")
            else:
                logging.info(f"[Node {self.port}] 数据文件 {self.data_file} 不存在，使用空存储")
        except Exception as e:
            logging.error(f"[Node {self.port}] 加载数据失败: {str(e)}")
            self.store = {}

    def _save_data(self):
        """保存键值数据到文件"""
        try:
            temp_file = self.data_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.store, f, ensure_ascii=False, indent=2)

            os.replace(temp_file, self.data_file)
            logging.info(f"[Node {self.port}] 数据已保存到 {self.data_file}")
        except Exception as e:
            logging.error(f"[Node {self.port}] 保存数据失败: {str(e)}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def _forward_request(self, method_name, request):
        """将请求转发给所有已知的对等节点"""
        logging.info(f"[Node {self.port}] 开始将 {method_name} 请求转发给 {len(self.peers)} 个对等节点")
        for addr, stub in self.peers.items():
            try:
                # 根据方法名选择调用哪个 stub 方法
                if method_name == 'Put':
                    # 注意：直接转发原始请求对象
                    response = stub.Put(request, timeout=1) # 设置1秒超时
                    logging.info(f"[Node {self.port}] 成功将 Put 请求转发给 {addr}: {response.message}")
                elif method_name == 'Delete':
                    # 注意：直接转发原始请求对象
                    response = stub.Delete(request, timeout=1) # 设置1秒超时
                    logging.info(f"[Node {self.port}] 成功将 Delete 请求转发给 {addr}: {response.message}")
                # Get 和 ListKeys 在这个阶段不转发
            except grpc.RpcError as e:
                logging.error(f"[Node {self.port}] 转发 {method_name} 请求给 {addr} 失败: {e.code()} - {e.details()}")
                # 在更复杂的系统中，这里可能需要处理节点离线、重试等
            except Exception as e:
                logging.error(f"[Node {self.port}] 转发 {method_name} 请求给 {addr} 时发生意外错误: {str(e)}")


    def Put(self, request, context):
        # 1. 本地存储
        self.store[request.key] = request.value
        self._save_data()
        logging.info(f"[Node {self.port}] 本地存储成功: {request.key}={request.value}")

        # 2. 尝试将请求转发给其他对等节点 (Best-Effort)
        #    注意：这里是异步调用的简单模拟，实际应该是并发或放入队列处理
        #    为了简单起见，我们这里直接同步调用转发
        self._forward_request('Put', request)

        return greeter_pb2.OperationResponse(
            success=True,
            message=f"[Node {self.port}] 成功存储并尝试转发: {request.key}={request.value}"
        )

    def Get(self, request, context):
        # Get 操作只读取本地数据
        logging.info(f"[Node {self.port}] 处理 Get 请求: key={request.key}")
        if request.key in self.store:
            return greeter_pb2.Value(value=self.store[request.key])
        
        logging.warning(f"[Node {self.port}] Get 请求的键不存在: {request.key}")
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"[Node {self.port}] 键不存在: {request.key}")
        return greeter_pb2.Value()

    def Delete(self, request, context):
        logging.info(f"[Node {self.port}] 处理 Delete 请求: key={request.key}")
        if request.key in self.store:
            # 1. 本地删除
            del self.store[request.key]
            self._save_data()
            logging.info(f"[Node {self.port}] 本地删除成功: {request.key}")

            # 2. 尝试将删除操作转发给其他对等节点
            self._forward_request('Delete', request)

            return greeter_pb2.OperationResponse(
                success=True,
                message=f"[Node {self.port}] 成功删除并尝试转发: {request.key}"
            )
        
        logging.warning(f"[Node {self.port}] Delete 请求的键不存在: {request.key}")
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"[Node {self.port}] 键不存在: {request.key}")
        return greeter_pb2.OperationResponse(success=False, message=f"[Node {self.port}] 删除失败，键不存在: {request.key}")


    def ListKeys(self, request, context):
        # ListKeys 操作也只列出本地的键
        logging.info(f"[Node {self.port}] 处理 ListKeys 请求")
        return greeter_pb2.KeyList(keys=list(self.store.keys()))

# 全局 server 实例，用于信号处理
_server_instance = None
_kv_store_instance = None

def handle_shutdown(signo, frame):
    global _server_instance, _kv_store_instance
    logging.info("正在关闭服务器...")
    if _server_instance:
        # 尝试优雅关闭，等待最多5秒让现有请求完成
        _server_instance.stop(5) 
    if _kv_store_instance:
        # 确保在关闭前保存最后的数据
        _kv_store_instance._save_data() 
    logging.info("服务器已关闭")
    sys.exit(0)

def serve():
    global _server_instance, _kv_store_instance

    # --- 解析命令行参数 ---
    parser = argparse.ArgumentParser(description='分布式键值存储节点')
    parser.add_argument('--port', type=int, required=True, help='当前节点监听的端口号')
    parser.add_argument('--peers', type=str, default="", help='其他对等节点的地址列表，用逗号分隔 (例如 "localhost:50052,localhost:50053")')
    args = parser.parse_args()

    port = args.port
    # 将逗号分隔的字符串转换为地址列表，并过滤掉空字符串
    peers_addr = [addr.strip() for addr in args.peers.split(',') if addr.strip()]
    
    listen_addr = f'localhost:{port}' # 明确监听地址

    # --- 服务器设置 ---
    # 创建 KeyValueStore 实例，传入端口和对等节点地址
    _kv_store_instance = KeyValueStore(port=port, peers_addr=peers_addr)

    # 创建 gRPC 服务器
    _server_instance = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeter_pb2_grpc.add_KeyValueStoreServicer_to_server(_kv_store_instance, _server_instance)

    _server_instance.add_insecure_port(listen_addr)
    _server_instance.start()

    logging.info(f"键值存储节点启动于 {listen_addr}, 对等节点: {peers_addr}")

    # --- 注册信号处理 ---
    signal.signal(signal.SIGINT, handle_shutdown)  # 处理 Ctrl+C
    signal.signal(signal.SIGTERM, handle_shutdown) # 处理 kill 命令

    # --- 等待服务器终止 ---
    try:
        # 使用 wait_for_termination() 阻塞主线程直到服务器停止
        _server_instance.wait_for_termination()
    except KeyboardInterrupt:
        # 虽然有信号处理，但以防万一也捕捉 KeyboardInterrupt
        handle_shutdown(signal.SIGINT, None)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    serve()