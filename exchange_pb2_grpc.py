# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import exchange_pb2 as exchange__pb2


class ExchangeServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Alive = channel.unary_unary(
                '/exchange.ExchangeService/Alive',
                request_serializer=exchange__pb2.Empty.SerializeToString,
                response_deserializer=exchange__pb2.ReviveInfo.FromString,
                )
        self.RequestHeartbeat = channel.unary_unary(
                '/exchange.ExchangeService/RequestHeartbeat',
                request_serializer=exchange__pb2.Empty.SerializeToString,
                response_deserializer=exchange__pb2.HeartbeatResponse.FromString,
                )
        self.ProposeCommit = channel.unary_unary(
                '/exchange.ExchangeService/ProposeCommit',
                request_serializer=exchange__pb2.CommitRequest.SerializeToString,
                response_deserializer=exchange__pb2.CommitVote.FromString,
                )
        self.SendVoteResult = channel.unary_unary(
                '/exchange.ExchangeService/SendVoteResult',
                request_serializer=exchange__pb2.CommitVote.SerializeToString,
                response_deserializer=exchange__pb2.Empty.FromString,
                )
        self.Ping = channel.unary_unary(
                '/exchange.ExchangeService/Ping',
                request_serializer=exchange__pb2.Empty.SerializeToString,
                response_deserializer=exchange__pb2.Empty.FromString,
                )
        self.SendOrder = channel.unary_unary(
                '/exchange.ExchangeService/SendOrder',
                request_serializer=exchange__pb2.OrderInfo.SerializeToString,
                response_deserializer=exchange__pb2.OrderId.FromString,
                )
        self.CancelOrder = channel.unary_unary(
                '/exchange.ExchangeService/CancelOrder',
                request_serializer=exchange__pb2.OrderId.SerializeToString,
                response_deserializer=exchange__pb2.Result.FromString,
                )
        self.GetOrderList = channel.unary_unary(
                '/exchange.ExchangeService/GetOrderList',
                request_serializer=exchange__pb2.Ticker.SerializeToString,
                response_deserializer=exchange__pb2.OrderList.FromString,
                )
        self.DepositCash = channel.unary_unary(
                '/exchange.ExchangeService/DepositCash',
                request_serializer=exchange__pb2.Deposit.SerializeToString,
                response_deserializer=exchange__pb2.Result.FromString,
                )
        self.OrderFill = channel.unary_unary(
                '/exchange.ExchangeService/OrderFill',
                request_serializer=exchange__pb2.UserInfo.SerializeToString,
                response_deserializer=exchange__pb2.FillInfo.FromString,
                )


class ExchangeServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Alive(self, request, context):
        """Connection functions
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestHeartbeat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ProposeCommit(self, request, context):
        """Voting functions
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendVoteResult(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Ping(self, request, context):
        """Client (broker) functions
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendOrder(self, request, context):
        """From institutions to exchange 
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOrderList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DepositCash(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def OrderFill(self, request, context):
        """From exchange to institutions, brokers
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ExchangeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Alive': grpc.unary_unary_rpc_method_handler(
                    servicer.Alive,
                    request_deserializer=exchange__pb2.Empty.FromString,
                    response_serializer=exchange__pb2.ReviveInfo.SerializeToString,
            ),
            'RequestHeartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestHeartbeat,
                    request_deserializer=exchange__pb2.Empty.FromString,
                    response_serializer=exchange__pb2.HeartbeatResponse.SerializeToString,
            ),
            'ProposeCommit': grpc.unary_unary_rpc_method_handler(
                    servicer.ProposeCommit,
                    request_deserializer=exchange__pb2.CommitRequest.FromString,
                    response_serializer=exchange__pb2.CommitVote.SerializeToString,
            ),
            'SendVoteResult': grpc.unary_unary_rpc_method_handler(
                    servicer.SendVoteResult,
                    request_deserializer=exchange__pb2.CommitVote.FromString,
                    response_serializer=exchange__pb2.Empty.SerializeToString,
            ),
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=exchange__pb2.Empty.FromString,
                    response_serializer=exchange__pb2.Empty.SerializeToString,
            ),
            'SendOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.SendOrder,
                    request_deserializer=exchange__pb2.OrderInfo.FromString,
                    response_serializer=exchange__pb2.OrderId.SerializeToString,
            ),
            'CancelOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelOrder,
                    request_deserializer=exchange__pb2.OrderId.FromString,
                    response_serializer=exchange__pb2.Result.SerializeToString,
            ),
            'GetOrderList': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOrderList,
                    request_deserializer=exchange__pb2.Ticker.FromString,
                    response_serializer=exchange__pb2.OrderList.SerializeToString,
            ),
            'DepositCash': grpc.unary_unary_rpc_method_handler(
                    servicer.DepositCash,
                    request_deserializer=exchange__pb2.Deposit.FromString,
                    response_serializer=exchange__pb2.Result.SerializeToString,
            ),
            'OrderFill': grpc.unary_unary_rpc_method_handler(
                    servicer.OrderFill,
                    request_deserializer=exchange__pb2.UserInfo.FromString,
                    response_serializer=exchange__pb2.FillInfo.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'exchange.ExchangeService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ExchangeService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Alive(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/Alive',
            exchange__pb2.Empty.SerializeToString,
            exchange__pb2.ReviveInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RequestHeartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/RequestHeartbeat',
            exchange__pb2.Empty.SerializeToString,
            exchange__pb2.HeartbeatResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ProposeCommit(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/ProposeCommit',
            exchange__pb2.CommitRequest.SerializeToString,
            exchange__pb2.CommitVote.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendVoteResult(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/SendVoteResult',
            exchange__pb2.CommitVote.SerializeToString,
            exchange__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/Ping',
            exchange__pb2.Empty.SerializeToString,
            exchange__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/SendOrder',
            exchange__pb2.OrderInfo.SerializeToString,
            exchange__pb2.OrderId.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CancelOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/CancelOrder',
            exchange__pb2.OrderId.SerializeToString,
            exchange__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetOrderList(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/GetOrderList',
            exchange__pb2.Ticker.SerializeToString,
            exchange__pb2.OrderList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DepositCash(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/DepositCash',
            exchange__pb2.Deposit.SerializeToString,
            exchange__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def OrderFill(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.ExchangeService/OrderFill',
            exchange__pb2.UserInfo.SerializeToString,
            exchange__pb2.FillInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class BrokerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.LogIn = channel.unary_unary(
                '/exchange.BrokerService/LogIn',
                request_serializer=exchange__pb2.UserInfo.SerializeToString,
                response_deserializer=exchange__pb2.Result.FromString,
                )
        self.LogOut = channel.unary_unary(
                '/exchange.BrokerService/LogOut',
                request_serializer=exchange__pb2.Empty.SerializeToString,
                response_deserializer=exchange__pb2.Result.FromString,
                )
        self.Register = channel.unary_unary(
                '/exchange.BrokerService/Register',
                request_serializer=exchange__pb2.UserInfo.SerializeToString,
                response_deserializer=exchange__pb2.Result.FromString,
                )
        self.SendOrder = channel.unary_unary(
                '/exchange.BrokerService/SendOrder',
                request_serializer=exchange__pb2.OrderInfo.SerializeToString,
                response_deserializer=exchange__pb2.OrderId.FromString,
                )
        self.CancelOrder = channel.unary_unary(
                '/exchange.BrokerService/CancelOrder',
                request_serializer=exchange__pb2.CancelRequest.SerializeToString,
                response_deserializer=exchange__pb2.Result.FromString,
                )
        self.GetBalance = channel.unary_unary(
                '/exchange.BrokerService/GetBalance',
                request_serializer=exchange__pb2.UserId.SerializeToString,
                response_deserializer=exchange__pb2.Balance.FromString,
                )
        self.DepositCash = channel.unary_unary(
                '/exchange.BrokerService/DepositCash',
                request_serializer=exchange__pb2.Deposit.SerializeToString,
                response_deserializer=exchange__pb2.Empty.FromString,
                )
        self.GetStocks = channel.unary_unary(
                '/exchange.BrokerService/GetStocks',
                request_serializer=exchange__pb2.UserId.SerializeToString,
                response_deserializer=exchange__pb2.UserStocks.FromString,
                )
        self.GetOrderList = channel.unary_unary(
                '/exchange.BrokerService/GetOrderList',
                request_serializer=exchange__pb2.Ticker.SerializeToString,
                response_deserializer=exchange__pb2.OrderList.FromString,
                )
        self.OrderFill = channel.unary_unary(
                '/exchange.BrokerService/OrderFill',
                request_serializer=exchange__pb2.UserInfo.SerializeToString,
                response_deserializer=exchange__pb2.BrokerFillInfo.FromString,
                )


class BrokerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def LogIn(self, request, context):
        """From user to broker
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LogOut(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBalance(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DepositCash(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStocks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOrderList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def OrderFill(self, request, context):
        """From broker to user
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BrokerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'LogIn': grpc.unary_unary_rpc_method_handler(
                    servicer.LogIn,
                    request_deserializer=exchange__pb2.UserInfo.FromString,
                    response_serializer=exchange__pb2.Result.SerializeToString,
            ),
            'LogOut': grpc.unary_unary_rpc_method_handler(
                    servicer.LogOut,
                    request_deserializer=exchange__pb2.Empty.FromString,
                    response_serializer=exchange__pb2.Result.SerializeToString,
            ),
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=exchange__pb2.UserInfo.FromString,
                    response_serializer=exchange__pb2.Result.SerializeToString,
            ),
            'SendOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.SendOrder,
                    request_deserializer=exchange__pb2.OrderInfo.FromString,
                    response_serializer=exchange__pb2.OrderId.SerializeToString,
            ),
            'CancelOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelOrder,
                    request_deserializer=exchange__pb2.CancelRequest.FromString,
                    response_serializer=exchange__pb2.Result.SerializeToString,
            ),
            'GetBalance': grpc.unary_unary_rpc_method_handler(
                    servicer.GetBalance,
                    request_deserializer=exchange__pb2.UserId.FromString,
                    response_serializer=exchange__pb2.Balance.SerializeToString,
            ),
            'DepositCash': grpc.unary_unary_rpc_method_handler(
                    servicer.DepositCash,
                    request_deserializer=exchange__pb2.Deposit.FromString,
                    response_serializer=exchange__pb2.Empty.SerializeToString,
            ),
            'GetStocks': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStocks,
                    request_deserializer=exchange__pb2.UserId.FromString,
                    response_serializer=exchange__pb2.UserStocks.SerializeToString,
            ),
            'GetOrderList': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOrderList,
                    request_deserializer=exchange__pb2.Ticker.FromString,
                    response_serializer=exchange__pb2.OrderList.SerializeToString,
            ),
            'OrderFill': grpc.unary_unary_rpc_method_handler(
                    servicer.OrderFill,
                    request_deserializer=exchange__pb2.UserInfo.FromString,
                    response_serializer=exchange__pb2.BrokerFillInfo.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'exchange.BrokerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class BrokerService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def LogIn(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/LogIn',
            exchange__pb2.UserInfo.SerializeToString,
            exchange__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def LogOut(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/LogOut',
            exchange__pb2.Empty.SerializeToString,
            exchange__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/Register',
            exchange__pb2.UserInfo.SerializeToString,
            exchange__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/SendOrder',
            exchange__pb2.OrderInfo.SerializeToString,
            exchange__pb2.OrderId.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CancelOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/CancelOrder',
            exchange__pb2.CancelRequest.SerializeToString,
            exchange__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetBalance(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/GetBalance',
            exchange__pb2.UserId.SerializeToString,
            exchange__pb2.Balance.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DepositCash(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/DepositCash',
            exchange__pb2.Deposit.SerializeToString,
            exchange__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetStocks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/GetStocks',
            exchange__pb2.UserId.SerializeToString,
            exchange__pb2.UserStocks.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetOrderList(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/GetOrderList',
            exchange__pb2.Ticker.SerializeToString,
            exchange__pb2.OrderList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def OrderFill(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/exchange.BrokerService/OrderFill',
            exchange__pb2.UserInfo.SerializeToString,
            exchange__pb2.BrokerFillInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
