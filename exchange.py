import socket, threading, time, grpc, pickle, os, sys, signal, multiprocessing
import exchange_pb2
from exchange_pb2_grpc import ExchangeServiceServicer, ExchangeServiceStub, add_ExchangeServiceServicer_to_server
from helpers import ThreadSafeSet
import constants as c
from concurrent import futures
from limit_order_book import LimitOrderBook
from database import Database, User
from collections import defaultdict, deque
from typing import Dict
        
# class that defines an exchange and its server
class ExchangeServer(ExchangeServiceServicer):
    def __init__(self, id: int, silent=False) -> None:
        self.ID = id
        self.SILENT = silent

        # initialize channel constants
        # self.HOST = socket.gethostbyname(socket.gethostname())
        self.HOST = "10.250.36.224"
        self.PORT = 50050 + self.ID

        # dict of the other servers' ports -> their host/ips
        self.PEER_PORTS : dict[int, str] = c.SERVER_IPS.copy()
        del self.PEER_PORTS[self.PORT]

        # dict of the other servers' ports -> bool determining if they are alive
        self.peer_alive = {port: False for port in self.PEER_PORTS}
        self.peer_stubs : dict[int, ExchangeServiceStub] = {}

        # identifies the leading server's port number
        self.primary_port = -1 
        
        # bool dictating if the current server is connected to the other (living) ones
        self.connected = False
        
        # thread to look for heartbeats from the other servers
        self.heartbeat_thread = threading.Thread(target = self.receive_heartbeat, daemon=True)
        self.stop_event = threading.Event()

        # init commit log file
        if not os.path.exists(c.LOG_DIR):
            os.makedirs(c.LOG_DIR)
        self.LOG_FILE_NAME = f"./{c.LOG_DIR}/server{self.ID}.log"
        self.log_file = open(self.LOG_FILE_NAME , "w")

        # init pkl file
        if not os.path.exists(c.PKL_DIR):
            os.makedirs(c.PKL_DIR)
        self.PKL_FILE_NAME = f"./{c.PKL_DIR}/server{self.ID}.pkl"
        
        # load the database (create if it does not exist)
        self.db = Database(filename=self.PKL_FILE_NAME)
    
        # thread safe set that tracks if a ballot id has been seen
        self.seen_ballots = ThreadSafeSet()
        

    # func "sprint": prints within a server
    def sprint(self, *args, **kwargs) -> None:
        if not self.SILENT:
            print(f"Server {self.ID}:", *args, **kwargs)

    # func "stop_server": stop the machine's heartbeat by setting stop_event
    def stop_server(self):
        self.stop_event.set() 
        self.heartbeat_thread.join()

    # (RE)CONNECTION SECTION

    # func "connect": connect current server to peers servers
    def connect(self) -> bool:
        if not self.connected:
            # Form a connection (stub) between all other peers (if they are alive)
            for port, host in self.PEER_PORTS.items():
                try:
                    # form connection (stub)
                    channel = grpc.insecure_channel(host + ':' + str(port)) 
                    self.peer_stubs[port] = ExchangeServiceStub(channel)
                    #  check if the peer is alive
                    revive_info: exchange_pb2.ReviveInfo = self.peer_stubs[port].Alive(exchange_pb2.Empty())

                    # if the primary peer has updates to share, update the current server
                    if revive_info.updates:
                        self.revive(revive_info)

                    self.peer_alive[port] = True
                except Exception as e:
                    self.sprint("Received Error in Connect:", e)
                    self.peer_alive[port] = False

        # run a leader election if the server has no primary
        if self.primary_port == -1:
            self.leader_election()

        self.connected = True
        self.sprint("Connected", self.peer_alive)
        return self.connected
    
    # func "revive": revive's a server based on the primary's commit log
    def revive(self, revive_info: exchange_pb2.ReviveInfo) -> None:
        self.primary_port = revive_info.primary_port

        self.sprint("Received primary: ", self.primary_port)

        try:
            # clear log file and rewrite with revive_info file !!
            self.log_file.truncate(0)
            self.log_file.write(revive_info.commit_log)
            self.log_file.flush()

            # update db to be like the log file OR use binary sent data to be the new db
            # TODO: probably should not cheese it like this ("this" being passing in bytes)
            self.db.turn_bytes_into_db(revive_info.db_bytes)

        except:
            self.sprint("Some log/db updating conflict")
    
    # rpc func "Alive": takes in Empty and returns updates
    def Alive(self, request, context):
        # only the primary can send over revive info (aka commit log)
        if self.primary_port == self.PORT:
            try:
                with open(self.LOG_FILE_NAME, 'r') as file:
                    text_data = file.read()
                with open(self.PKL_FILE_NAME, 'rb') as dbfile:
                    db_bytes = pickle.dumps(pickle.load(dbfile))
            except:
                text_data = ""
                db_bytes = bytes()
            return exchange_pb2.ReviveInfo(
                primary_port = self.primary_port, 
                commit_log = text_data,
                db_bytes = db_bytes, 
                updates = True)
        else:
            return exchange_pb2.ReviveInfo(updates = False)
    
    # HEARTBEAT SECTION
    
    # func "receive_heartbeat": ask all other machines if they are alive by asking of
    def receive_heartbeat(self) -> None:

        def individual_heartbeat(port: int) -> None:
            # every HEARTRATE seconds, ask given port for heartbeats
            stub = self.peer_stubs[port]
            while not self.stop_event.is_set():
                time.sleep(c.HEARTRATE)
                try:
                    response : exchange_pb2.HeartbeatResponse = stub.RequestHeartbeat(exchange_pb2.Empty())
                    if self.peer_alive[response.port] == False:
                        self.sprint(f"{response.port} is back online")
                    self.peer_alive[response.port] = True
                except:
                    # if cannot connect to a peer, mark it as dead
                    if self.peer_alive[port]:
                        self.sprint(f"Heartbeat not received from port {port}")
                    self.peer_alive[port] = False
                    if self.primary_port == port: # run an election if the primary has died 
                        self.leader_election()

        for port in self.peer_stubs:
            threading.Thread(target = individual_heartbeat, args=(port, ), daemon=True).start()

    # rpc func "RequestHeartbeat": takes Empty as input and retuns its port
    def RequestHeartbeat(self, request, context):
        return exchange_pb2.HeartbeatResponse(port=self.PORT)

    # func "leader_election": uses the bully algorithm to elect the machine with the lowest port as the leader
    def leader_election(self) -> int:
        alive_ports = (port for port, alive in [*self.peer_alive.items(), (self.PORT, True)] if alive)
        self.primary_port = min(alive_ports)
        self.sprint(f"New primary: {self.primary_port}")
        return self.primary_port

    # CONSENSUS VOTING (PAXOS) SECTION

    # func "send_commit_proposal" : proposes a commit, if all peers agree on it: it is commited; else: it is rejected
    def send_commit_proposal(self, commit: str) -> bool:

        # sets the ballot id to the largest unseen ballot
        ballot_id = self.seen_ballots.max() + 1
        self.seen_ballots.add(ballot_id)
        
        approved = True
        living_stubs = lambda: [(self.peer_stubs[port], port) for port in self.peer_alive if self.peer_alive[port]]

        # sends the commit request to all living peers and tallies their responses
        for stub, port in living_stubs():
            req = exchange_pb2.CommitRequest(commit = commit, ballot_id = ballot_id)
            try:
                response : exchange_pb2.CommitVote = stub.ProposeCommit(req)
                approved &= response.approve
            except:
                self.sprint(port, "died when voting; vote rejected")
                approved = False
                self.peer_alive[port] = False

        # sends the result of the vote to all living peers
        for stub, port in living_stubs():

            vote = exchange_pb2.CommitVote(commit = commit, approve = approved, ballot_id = ballot_id)
            try:
                stub.SendVoteResult(vote)
            except:
                self.sprint(port, "died when confirming vote")
                self.peer_alive[port] = False

        # commits changes if vote was approved
        if approved:
            # add commit
            self.write_to_log(commit, ballot_id)
        else:
            self.sprint("*Rejected commit")

        return approved

    # rpc func "ProposeCommit": takes a CommitRequest/Proposal as input, returns an approving vote iff the ballot id is unseen
    def ProposeCommit(self, request, context):
        approved = request.ballot_id not in self.seen_ballots
        self.seen_ballots.add(request.ballot_id)
        return exchange_pb2.CommitVote(approve = approved)
    
    # rpc func "SendVoteResult": takes a CommitVote/Final verdict as input, adds commit if approved, returns Empty
    def SendVoteResult(self, request, context):
        if request.approve:
            # add commit
            commit, ballot_id = request.commit, request.ballot_id
            self.write_to_log(commit, ballot_id)
            commands = commit.split(c.DIVIDER)
            for cmd in commands:
                try:
                    exec(cmd)
                except Exception as e:
                    print(f"Error from Paxos: {e}")
            self.db.store_data()
        else:
            self.sprint("Rejected commit")

        return exchange_pb2.Empty()
    
    # func "write_to_log": writes a commit to the log file
    def write_to_log(self, commit, ballot_id):
        # TODO: if not connected, wait until connected to add these commits
        self.sprint(f"Added commit {commit} w/ ballot_id {ballot_id}")
        self.log_file.write(f"{ballot_id}# {commit}\n")
        self.log_file.flush()

    # func "vote_on_client_request": initiates a vote between servers
    def vote_on_client_request(self, commit_state: str) -> bool:

        for _ in range(c.MAX_VOTE_ATTEMPTS):
            if self.send_commit_proposal(commit_state):
                return True
                
        return False

    # CLIENT FUNCTIONS SECTION

    # decorator that only allows clients to connect if the current machine is connected to the peers
    def connection_required(func):
        def wrapper(self, request, context):

            if not self.connected:
                context.set_details("Server currently disconnected.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return grpc.RpcMethodHandler()
            
            return func(self, request, context)
        
        return wrapper

    # WIP
    # rpc func "SendOrder": push an order to the orderbooks, make matches if possible
    @connection_required
    def SendOrder(self, request, context):
        # retrieve the order
        ticker = request.ticker
        quantity = request.quantity
        price = request.price
        uid = request.uid
        side = "bid" if request.type == exchange_pb2.OrderType.BID else "ask"

        # PAXOS
        state_str = f"""self.send_order_helper('{ticker}', {quantity}, {price}, {uid}, '{side}')"""
        if not self.vote_on_client_request(state_str):
            return exchange_pb2.OrderId(oid=-1)

        new_oid = self.send_order_helper(ticker, quantity, price, uid, side)

        return exchange_pb2.OrderId(oid=new_oid)
    
    def send_order_helper(self, ticker, quantity, price, uid, side):
        # retreive orderbook associated with the stock's ticker
        book = self.db.get_db()["orderbooks"][ticker]
        
        new_oid = self.db.get_db()["oid_count"]
        self.db.get_db()["oid_count"] += 1

        self.db.get_db()["oid_to_ticker"][new_oid] =  ticker
        
        filled_orders = book.add_order(side, price, quantity, uid, new_oid)
        
        for filled_order in filled_orders:
            bid_uid, ask_uid, execution_price, executed_quantity, bid_oid, ask_oid = filled_order
            
            self.db.get_db()["uid_to_user_dict"][bid_uid].balance -= executed_quantity * execution_price

            self.db.get_db()["uid_to_user_dict"][bid_uid].ticker_to_amount[ticker] = self.db.get_db()["uid_to_user_dict"][bid_uid].ticker_to_amount.get(ticker, 0) + executed_quantity
            self.db.get_db()["uid_to_user_dict"][bid_uid].filled_oids.append((bid_oid, execution_price, executed_quantity))

            if ask_oid != -1:
                self.db.get_db()["uid_to_user_dict"][ask_uid].balance += executed_quantity * execution_price
                self.db.get_db()["uid_to_user_dict"][ask_uid].ticker_to_amount[ticker] -= executed_quantity
                self.db.get_db()["uid_to_user_dict"][ask_uid].filled_oids.append((ask_oid, execution_price, executed_quantity))
        
        self.db.store_data()   

        book.print_orderbook()

        return new_oid 

    # rpc func "CancelOrder": 
    @connection_required
    def CancelOrder(self, request, context) -> exchange_pb2.Result:
        # request = exchange_pb2.OrderId
        if request.oid not in self.db.get_db()["oid_to_ticker"].keys():
            return exchange_pb2.Result(result=False)
        
        if request.oid < 0:
            return exchange_pb2.Result(result=False)
        
        ticker = self.db.get_db()["oid_to_ticker"][request.oid]
    
        # PAXOS
        state_str = f'self.db.get_db()["orderbooks"]["{ticker}"].cancel_order_by_oid({request.oid})'
        if not self.vote_on_client_request(state_str):
            return exchange_pb2.Result(result=False, message = "Servers failed to reach agreement on cancel request")

        book = self.db.get_db()["orderbooks"][ticker]
        result = book.cancel_order_by_oid(request.oid)
        self.db.store_data()

        book.print_orderbook()

        return exchange_pb2.Result(result=result)
    
    # WIP TODO
    # rpc func "GetOrderList": 
    # could probably skip this for now tbh
    @connection_required
    def GetOrderList(self, request, context) -> exchange_pb2.OrderInfo:
        book = self.db.get_db()["orderbooks"]["GOOGL"]
        return book.get_orderbook()

    # rpc func "DepositCash": 
    @connection_required
    def DepositCash(self, request, context) -> exchange_pb2.Result:
        res = False
        state_str = f"self.db.get_db()['client_balance'][{request.uid}] += {request.amount}"
        if request.uid in self.db.get_db()["client_balance"] and self.vote_on_client_request(state_str):
            self.db.get_db()["client_balance"][request.uid] += request.amount
            self.db.store_data()
            res = True  
                
        return exchange_pb2.Result(result = res)

    # rpc func "OrderFill":
    @connection_required
    def OrderFill(self, request, context) -> exchange_pb2.FillInfo:
        # print("OrderFill called")
        failure = exchange_pb2.FillInfo(oid=-1, 
                                        amount_filled=-1, 
                                        execution_price=-1)

        if request.uid not in self.db.get_db()["uid_to_user_dict"].keys():
            # self.sprint("UID not in keys")
            return failure
        
        user = self.db.get_db()["uid_to_user_dict"][request.uid]
        if len(user.filled_oids) == 0:
            # self.sprint(f"No filled oids for user {request.uid}")
            return failure 
        
        # PAXOS
        state_str = f"""self.db.get_db()["uid_to_user_dict"][{request.uid}].filled_oids.popleft()"""
        if not self.vote_on_client_request(state_str):
            self.sprint("PAXOS consensus failed")
            return failure

        oid, execution_price, quantity = user.filled_oids.popleft()
        self.db.store_data()

        return exchange_pb2.FillInfo(oid=oid, 
                                     amount_filled=quantity, 
                                     execution_price=execution_price)

    # rpc func "Ping": allows client to 
    @connection_required
    def Ping(self, request, context):
        return exchange_pb2.Empty()

# func "serve": starts an exchange server
def serve(id):
    exchange = ExchangeServer(id)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_ExchangeServiceServicer_to_server(exchange, server)
    server.add_insecure_port(exchange.HOST + ':' + str(exchange.PORT))
    server.start()
    exchange.sprint(f"Server initialized at {exchange.HOST} on port {exchange.PORT}")
    time.sleep(3)
    exchange.connect()
    exchange.heartbeat_thread.start()
    server.wait_for_termination()

# clean control c exiting
def sigint_handler(signum, frame):
    # terminate all child processes
    for process in multiprocessing.active_children():
        process.terminate()
    # exit the main process without raising SystemExit
    try:
        sys.exit(0)
    except SystemExit:
        pass

def main():
    # Allow for server creation by id through command-line args
    if len(sys.argv) == 2:
        try:
            machine_id = int(sys.argv[1])
            connection_wait_time = 5
            serve(machine_id)
        except KeyboardInterrupt:
            pass
    else:
        processes = []
    
        # Spawns a new process for each server that we have to run 
        for i in range(c.NUM_SERVERS):
            process = multiprocessing.Process(target=serve, args=(i, ))
            processes.append(process)

        # Allow for ctrl-c exiting
        signal.signal(signal.SIGINT, sigint_handler)

        # Starts each process
        for process in processes:
            process.start()

if __name__ == '__main__':
    # Get your own hostname:
    # hostname = socket.gethostbyname(socket.gethostname())
    hostname = "10.250.36.224"
    print("Hostname:", hostname)
    main()