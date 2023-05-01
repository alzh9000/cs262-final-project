import socket, threading, time, grpc, os
import exchange_pb2
from exchange_pb2_grpc import BrokerServiceStub
import constants as c
from typing import Dict, List, Tuple, Set, Optional
from concurrent import futures

class BrokerClient():
    def __init__(self, channel):
        self.stub = BrokerServiceStub(channel)
        self.uid: Optional[int]
    
    def Register(self, uid) -> None:
        result = self.stub.Register(exchange_pb2.UserInfo(uid=int(uid)))
        if result.result:
            print("Successfully registered")
            self.uid = int(uid)
        else:
            print("Error while registering")
    
    def DepositCash(self, amount) -> None:
        if not self.uid:
            print("Please register/log in first.")
            return

        # Deposit cash; this returns Empty
        self.stub.DepositCash(exchange_pb2.Deposit(uid=self.uid, 
                                                   amount=amount))
        
    def SendOrder(self, order_type, ticker, quantity, price, uid) -> None:

        result = self.stub.SendOrder(exchange_pb2.OrderInfo(ticker=ticker, 
                                                            quantity=quantity,
                                                            price=price,
                                                            uid=self.uid,
                                                            type=order_type))
        if result.oid == -1:
            print("Order failed!")
        else:
            print(f"Order placed. Order id: {result.oid}")

    def CancelOrder(self, oid) -> None:
        self.stub.CancelOrder(exchange_pb2.CancelRequest(uid=self.uid, oid=oid))

    def make_order(self) -> None:
        if not self.uid:
            print("Please log in first before using that action.")
            return

        print("Would you like to buy or sell a stock?")
        print("[1] Buy")
        print("[2] Sell")
        inp = input("> ")
        order_type = None
        if inp == "1":
            order_type = exchange_pb2.OrderType.BID
        elif inp == "2":
            order_type = exchange_pb2.OrderType.ASK
        else:
            print("Please enter 1 or 2.")
            return

        print("For which stock?")
        ticker = input("> ")

        print("And how many shares?")
        quantity = int(input("> "))

        print("For what price for each share?")
        price = int(input("> "))
        # send information to the broker client
        self.SendOrder(order_type, ticker, quantity, price, self.uid)

if __name__ == "__main__":
    channel = grpc.insecure_channel(c.BROKER_IP[1] + ':' + str(c.BROKER_IP[0]))
    client = BrokerClient(channel)
    while True:
        print("[1] Register\n[2] Buy/Sell\n[3] Deposit Cash")
        inp = input("> ")
        if inp == '1':
            print("What uid?")
            uid = input("> ")
            client.Register(uid)
        elif inp == '2':
            client.make_order()
        else:
            print("How much?")
            amount = input("> ")
            client.DepositCash(int(amount))
