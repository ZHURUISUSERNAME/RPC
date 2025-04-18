# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import greeter_pb2 as greeter__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in greeter_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class KeyValueStoreStub(object):
    """定义键值存储服务
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Put = channel.unary_unary(
                '/greeter.KeyValueStore/Put',
                request_serializer=greeter__pb2.KeyValue.SerializeToString,
                response_deserializer=greeter__pb2.OperationResponse.FromString,
                _registered_method=True)
        self.Get = channel.unary_unary(
                '/greeter.KeyValueStore/Get',
                request_serializer=greeter__pb2.Key.SerializeToString,
                response_deserializer=greeter__pb2.Value.FromString,
                _registered_method=True)
        self.Delete = channel.unary_unary(
                '/greeter.KeyValueStore/Delete',
                request_serializer=greeter__pb2.Key.SerializeToString,
                response_deserializer=greeter__pb2.OperationResponse.FromString,
                _registered_method=True)
        self.ListKeys = channel.unary_unary(
                '/greeter.KeyValueStore/ListKeys',
                request_serializer=greeter__pb2.Empty.SerializeToString,
                response_deserializer=greeter__pb2.KeyList.FromString,
                _registered_method=True)


class KeyValueStoreServicer(object):
    """定义键值存储服务
    """

    def Put(self, request, context):
        """存储键值对
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """获取键对应的值
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """删除键值对
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListKeys(self, request, context):
        """列出所有键
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_KeyValueStoreServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=greeter__pb2.KeyValue.FromString,
                    response_serializer=greeter__pb2.OperationResponse.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=greeter__pb2.Key.FromString,
                    response_serializer=greeter__pb2.Value.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=greeter__pb2.Key.FromString,
                    response_serializer=greeter__pb2.OperationResponse.SerializeToString,
            ),
            'ListKeys': grpc.unary_unary_rpc_method_handler(
                    servicer.ListKeys,
                    request_deserializer=greeter__pb2.Empty.FromString,
                    response_serializer=greeter__pb2.KeyList.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'greeter.KeyValueStore', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('greeter.KeyValueStore', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class KeyValueStore(object):
    """定义键值存储服务
    """

    @staticmethod
    def Put(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/greeter.KeyValueStore/Put',
            greeter__pb2.KeyValue.SerializeToString,
            greeter__pb2.OperationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/greeter.KeyValueStore/Get',
            greeter__pb2.Key.SerializeToString,
            greeter__pb2.Value.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/greeter.KeyValueStore/Delete',
            greeter__pb2.Key.SerializeToString,
            greeter__pb2.OperationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListKeys(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/greeter.KeyValueStore/ListKeys',
            greeter__pb2.Empty.SerializeToString,
            greeter__pb2.KeyList.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
