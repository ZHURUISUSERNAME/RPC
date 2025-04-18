from concurrent import futures
import logging
import time
import grpc
import json
import os
import greeter_pb2
import greeter_pb2_grpc

DATA_FILE = "kv_store.json"

class KeyValueStore(greeter_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.store = self._load_data()  # 初始化时加载数据

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
        return {}

    def _save_data(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.store, f)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def Put(self, request, context):
        print(f"Put操作: key={request.key}, value={request.value}")
        self.store[request.key] = request.value
        self._save_data()  # 立即保存数据
        return greeter_pb2.OperationResponse(
            success=True,
            message=f"成功存储键值对: {request.key}={request.value}"
        )

    def Get(self, request, context):
        print(f"Get操作: key={request.key}")
        if request.key in self.store:
            return greeter_pb2.Value(value=self.store[request.key])
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"键 {request.key} 不存在")
        return greeter_pb2.Value()

    def Delete(self, request, context):
        print(f"Delete操作: key={request.key}")
        if request.key in self.store:
            del self.store[request.key]
            self._save_data()  # 立即保存数据
            return greeter_pb2.OperationResponse(
                success=True,
                message=f"成功删除键: {request.key}"
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"键 {request.key} 不存在")

    def ListKeys(self, request, context):
        print("ListKeys操作")
        return greeter_pb2.KeyList(keys=list(self.store.keys()))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeter_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStore(), server)
    server.add_insecure_port('[::]:50051')
    print("键值存储服务器启动，监听端口 50051...")
    server.start()
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("服务器停止中...")
        server.stop(0)
        # 保存数据
        KeyValueStore()._save_data()
        print("数据已保存")
        print("服务器已停止。")

# Python 的标准入口点检查
if __name__ == '__main__':
    logging.basicConfig() # 配置基本的日志记录
    serve()             # 调用启动服务器的函数
