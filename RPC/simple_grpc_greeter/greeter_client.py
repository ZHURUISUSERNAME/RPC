import logging
import grpc
import greeter_pb2
import greeter_pb2_grpc

def print_menu():
    print("\n键值存储客户端")
    print("1. 存储键值对")
    print("2. 获取值")
    print("3. 删除键值对")
    print("4. 列出所有键")
    print("5. 退出")

def run():
    print("尝试连接到键值存储服务器 localhost:50051 ...")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = greeter_pb2_grpc.KeyValueStoreStub(channel)

        while True:
            print_menu()
            choice = input("请选择操作: ")

            if choice == "1":  # Put
                key = input("输入键: ")
                value = input("输入值: ")
                try:
                    response = stub.Put(greeter_pb2.KeyValue(key=key, value=value))
                    print(f"操作结果: {response.message}")
                except grpc.RpcError as e:
                    print(f"错误: {e.details()}")

            elif choice == "2":  # Get
                key = input("输入键: ")
                try:
                    response = stub.Get(greeter_pb2.Key(key=key))
                    print(f"获取的值: {response.value}")
                except grpc.RpcError as e:
                    print(f"错误: {e.details()}")

            elif choice == "3":  # Delete
                key = input("输入要删除的键: ")
                try:
                    response = stub.Delete(greeter_pb2.Key(key=key))
                    print(f"操作结果: {response.message}")
                except grpc.RpcError as e:
                    print(f"错误: {e.details()}")

            elif choice == "4":  # ListKeys
                try:
                    response = stub.ListKeys(greeter_pb2.Empty())
                    print("所有键:")
                    for key in response.keys:
                        print(f"- {key}")
                except grpc.RpcError as e:
                    print(f"错误: {e.details()}")

            elif choice == "5":  # Exit
                print("退出客户端")
                break

            else:
                print("无效选择，请重试")

if __name__ == '__main__':
    logging.basicConfig()
    run()
