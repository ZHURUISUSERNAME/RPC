from concurrent import futures
import logging
import time
import grpc
import json
import os
import greeter_pb2
import greeter_pb2_grpc
import signal

# 使用绝对路径存储数据文件
DATA_FILE = os.path.join(os.path.dirname(__file__), "kv_store.json")

class KeyValueStore(greeter_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.store = {}
        self._load_data()

    def _load_data(self):
        """加载持久化的键值数据"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.store = json.load(f)
                logging.info(f"成功从 {DATA_FILE} 加载了 {len(self.store)} 条数据")
            else:
                logging.info("数据文件不存在，使用空存储")
        except Exception as e:
            logging.error(f"加载数据失败: {str(e)}")
            self.store = {}

    def _save_data(self):
        """保存键值数据到文件"""
        try:
            temp_file = DATA_FILE + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.store, f, ensure_ascii=False, indent=2)
            
            # 原子方式替换文件
            os.replace(temp_file, DATA_FILE)
            logging.info(f"数据已保存到 {DATA_FILE}")
        except Exception as e:
            logging.error(f"保存数据失败: {str(e)}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def Put(self, request, context):
        self.store[request.key] = request.value
        self._save_data()
        return greeter_pb2.OperationResponse(
            success=True,
            message=f"成功存储: {request.key}={request.value}"
        )

    def Get(self, request, context):
        if request.key in self.store:
            return greeter_pb2.Value(value=self.store[request.key])
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"键不存在: {request.key}")
        return greeter_pb2.Value()

    def Delete(self, request, context):
        if request.key in self.store:
            del self.store[request.key]
            self._save_data()
            return greeter_pb2.OperationResponse(
                success=True,
                message=f"成功删除: {request.key}"
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"键不存在: {request.key}")
        return greeter_pb2.OperationResponse(success=False)

    def ListKeys(self, request, context):
        return greeter_pb2.KeyList(keys=list(self.store.keys()))

def serve():
    # 创建服务器实例
    kv_store = KeyValueStore()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeter_pb2_grpc.add_KeyValueStoreServicer_to_server(kv_store, server)
    
    # 明确使用 localhost 地址
    server.add_insecure_port('localhost:50051')
    server.start()
    
    logging.info("键值存储服务器启动于 localhost:50051")

    # 注册信号处理
    def handle_shutdown(signo, frame):
        logging.info("正在关闭服务器...")
        server.stop(5)
        kv_store._save_data()
        logging.info("服务器已关闭")
        import sys
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        handle_shutdown(None, None)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    serve()