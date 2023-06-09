import socket, threading, time, grpc, pickle, os, sys, signal, multiprocessing, random
import exchange_pb2
from exchange_pb2_grpc import ExchangeServiceServicer, ExchangeServiceStub, add_ExchangeServiceServicer_to_server
from helpers import ThreadSafeSet, sigint_handler
import constants as c
from concurrent import futures
from database import Database
from typing import List
        
# class to define an exchange server
class ExchangeServer(ExchangeServiceServicer):
    def __init__(self, id: int, silent=False) -> None:
        self.ID = id
        self.SILENT = silent
        self.DEBUG = False

        # initialize channel constants
        self.PORT = 50050 + self.ID
        self.HOST = c.SERVER_IPS[self.PORT]

        # dict of the other servers' ports -> their host/ips
        self.PEER_PORTS : dict[int, str] = {k: c.SERVER_IPS[k] for k in list(c.SERVER_IPS)[:c.NUM_SERVERS]}
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

    # func "debug_print": debug print within a server
    def debug_print(self, *args, **kwargs) -> None:
        # only print if in debug mode
        if self.DEBUG:
            print(f"Server {self.ID}:", *args, **kwargs)

    # func "stop_server": stop the machine's heartbeat by setting stop_event
    def stop_server(self):
        self.stop_event.set() 
        self.heartbeat_thread.join()

    #### (RE)CONNECTION SECTION ####

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
                    self.sprint(f"Connected to peer {port}")
                except Exception as e:
                    self.sprint("Received connect error:", e)
                    self.peer_alive[port] = False

        # run a leader election if the server has no primary
        if self.primary_port == -1:
            self.leader_election()

        self.connected = True
        self.sprint("Connected:", self.peer_alive)
        return self.connected
    
    # func "revive": revive's a server based on revive info from primary server
    def revive(self, revive_info: exchange_pb2.ReviveInfo) -> None:
        self.primary_port = revive_info.primary_port

        self.debug_print("Received primary:", self.primary_port)

        try:
            # clear log file and rewrite with revive_info file !!
            self.log_file.truncate(0)
            self.log_file.write(revive_info.commit_log)
            self.log_file.flush()

            # update db using revive info
            self.db.turn_bytes_into_db(revive_info.db_bytes)
            
            self.sprint("Server revived", self.primary_port)
        except:
            self.sprint("Some log/db updating conflict")
    
    # rpc func "Alive": takes in Empty and returns updates
    def Alive(self, request, context):

        # only the primary can send over revive info
        if self.primary_port == self.PORT:
            try:
                with open(self.LOG_FILE_NAME, 'r') as file:
                    text_data = file.read()
                with open(self.PKL_FILE_NAME, 'rb') as dbfile:
                    db_bytes = pickle.dumps(pickle.load(dbfile))
            except:
                text_data = ""
                db_bytes = bytes()
            info = exchange_pb2.ReviveInfo(
                primary_port = self.primary_port, 
                commit_log = text_data,
                db_bytes = db_bytes, 
                updates = True)
        else:
            info = exchange_pb2.ReviveInfo(updates = False)

        return info
    
    #### HEARTBEAT SECTION ####
    
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
        self.sprint("New primary:", self.primary_port)
        return self.primary_port

    #### CONSENSUS VOTING (PAXOS) SECTION ####

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
        approved = request.ballot_id > self.seen_ballots.max()
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
                    self.sprint(f"Error from Paxos in SendVoteResult: {e}")
            self.db.store_data()
        else:
            self.sprint("Rejected commit in SendVoteResult")

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
            time.sleep(random.uniform(0, 1) / 10)
                
        return False

    #### CLIENT (BROKER/INSTITUTION) FUNCTIONS SECTION ####

    # decorator that only allows clients to connect if the current machine is connected to the peers
    def connection_required(func):
        def wrapper(self, request, context):

            if not self.connected:
                context.set_details("Server currently disconnected.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return grpc.RpcMethodHandler()
            
            start_time = time.time()
            res = func(self, request, context)
            latency = time.time() - start_time
            
            return res
        
        return wrapper

    # rpc func "SendOrder": push an order to the orderbooks, make matches if possible
    @connection_required
    def SendOrder(self, request, context):
        self.debug_print("[SendOrder]", "Starting RPC")

        # retrieve the order
        ticker = request.ticker
        quantity = request.quantity
        price = request.price
        uid = request.uid
        side = "bid" if request.type == exchange_pb2.OrderType.BID else "ask"

        # run PAXOS to ensure consensus when adding order
        state_str = f"""self.send_order_helper('{ticker}', {quantity}, {price}, {uid}, '{side}')"""
        if not self.vote_on_client_request(state_str):
            return exchange_pb2.OrderId(oid=-1)

        new_oid = self.send_order_helper(ticker, quantity, price, uid, side)

        self.debug_print("[SendOrder]", "Exiting successfully")
        return exchange_pb2.OrderId(oid=new_oid)
    
    # func "send_order_helper":  add order to orderbook, fill matches, return its oid.
    def send_order_helper(self, ticker, quantity, price, uid, side) -> int:

        # retreive orderbook associated with the stock's ticker
        self.debug_print("[send_order_helper]", f"Retreiving {ticker} orderbook")
        book = self.db.get_db()["orderbooks"][ticker]

        # increment oid_count to make order unique
        new_oid = self.db.get_db()["oid_count"]
        self.db.get_db()["oid_count"] += 1
        self.db.get_db()["oid_to_ticker"][new_oid] =  ticker

        # add the order to the orderbook and retrive filled orders
        self.debug_print("[send_order_helper]", "Adding order to book and run matching")
        filled_orders = book.add_order(side, price, quantity, uid, new_oid)
        self.debug_print("[send_order_helper]", "Filled orders:", filled_orders)
        
        # for each matched order, change each bid/ask user's account
        for filled_order in filled_orders:
            bid_uid, ask_uid, execution_price, executed_quantity, bid_oid, ask_oid = filled_order
            
            # BID USERS
            self.debug_print("[send_order_helper]", f"Modifying bid user {bid_uid}'s account")
            self.db.get_db()["uid_to_user_dict"][bid_uid].balance -= executed_quantity * execution_price
            self.db.get_db()["uid_to_user_dict"][bid_uid].ticker_to_amount[ticker] = self.db.get_db()["uid_to_user_dict"][bid_uid].ticker_to_amount.get(ticker, 0) + executed_quantity
            self.db.get_db()["uid_to_user_dict"][bid_uid].filled_oids.append((bid_oid, execution_price, executed_quantity))

            # ASK USERS
            if ask_oid != -1: # accounting for orderbook's default asks
                self.debug_print("[send_order_helper]", f"Modifying ask user {ask_uid}'s account")
                self.db.get_db()["uid_to_user_dict"][ask_uid].balance += executed_quantity * execution_price
                self.db.get_db()["uid_to_user_dict"][ask_uid].ticker_to_amount[ticker] -= executed_quantity
                self.db.get_db()["uid_to_user_dict"][ask_uid].filled_oids.append((ask_oid, execution_price, executed_quantity))

        self.db.store_data()   
        self.debug_print("[send_order_helper]", "Resulting orderbook:", book)
        return new_oid 

    # rpc func "CancelOrder": 
    @connection_required
    def CancelOrder(self, request, context) -> exchange_pb2.Result:
        self.debug_print("[CancelOrder]", "Starting RPC")

        if request.oid not in self.db.get_db()["oid_to_ticker"].keys():
            self.debug_print("[CancelOrder]", f"Order {request.oid} not found")
            return exchange_pb2.Result(result=False)
        
        if request.oid < 0:
            self.debug_print("[CancelOrder]", f"Negative orders not allowed")
            return exchange_pb2.Result(result=False)
        
        self.debug_print("[CancelOrder]", f"Order {request.oid} found")
        ticker = self.db.get_db()["oid_to_ticker"][request.oid]
    
        # run PAXOS to ensure consensus when deleting order
        state_str = f'self.db.get_db()["orderbooks"]["{ticker}"].cancel_order_by_oid({request.oid})'
        if not self.vote_on_client_request(state_str):
            return exchange_pb2.Result(result=False, message = "Servers failed to reach agreement on cancel request")

        book = self.db.get_db()["orderbooks"][ticker]
        result = book.cancel_order_by_oid(request.oid)
        self.db.store_data()
        self.debug_print("[CancelOrder]", "Resulting orderbook:", book)
        self.debug_print("[CancelOrder]", "Exiting successfully")
        return exchange_pb2.Result(result=result)
    
    @connection_required
    def GetOrderList(self, request, context):
        if request.ticker not in self.db.get_db()["orderbooks"].keys():
            return exchange_pb2.OrderList(pickle=bytes())
        book = self.db.get_db()["orderbooks"]["GOOGL"]
        pickled = pickle.dumps(book)
        return exchange_pb2.OrderList(pickle=pickled)

    # rpc func "DepositCash": 
    @connection_required
    def DepositCash(self, request, context) -> exchange_pb2.Result:
        self.debug_print("[DepositCash]", "Starting RPC")
        
        # run PAXOS to maintain user account consensus
        res = False
        state_str = f"self.db.get_db()['client_balance'][{request.uid}] += {request.amount}"
        if request.uid in self.db.get_db()["client_balance"] and self.vote_on_client_request(state_str):
            self.db.get_db()["client_balance"][request.uid] += request.amount
            self.db.store_data()
            res = True  

        self.debug_print("[DepositCash]", "Exiting successfully")       
        return exchange_pb2.Result(result = res)

    # rpc func "OrderFill":
    @connection_required
    def OrderFill(self, request, context) -> exchange_pb2.FillInfo:
        # self.debug_print("[OrderFill]", "Starting RPC")
        failure = exchange_pb2.FillInfo(oid=-1, 
                                        amount_filled=-1, 
                                        execution_price=-1)

        if request.uid not in self.db.get_db()["uid_to_user_dict"].keys():
            # self.debug_print("[OrderFill]", "UID not in keys")
            return failure
        
        user = self.db.get_db()["uid_to_user_dict"][request.uid]
        if len(user.filled_oids) == 0:
            # self.debug_print("[OrderFill]", f"No filled oids for user {request.uid}")
            return failure 
        
        # run PAXOS to ensure order fills are accounted for in db
        state_str = f"""self.db.get_db()["uid_to_user_dict"][{request.uid}].filled_oids.popleft()"""
        if not self.vote_on_client_request(state_str):
            self.sprint("PAXOS consensus failed in OrderFill")
            return failure

        oid, execution_price, quantity = user.filled_oids.popleft()
        self.db.store_data()

        # self.debug_print("[OrderFill]", "Exiting successfully")  
        return exchange_pb2.FillInfo(oid=oid, 
                                     amount_filled=quantity, 
                                     execution_price=execution_price)

    # rpc func "Ping": allows client to 
    @connection_required
    def Ping(self, request, context):
        return exchange_pb2.Empty()

# func "serve": starts an exchange server
def serve(id, silent=False):
    exchange = ExchangeServer(id, silent=silent)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_ExchangeServiceServicer_to_server(exchange, server)
    server.add_insecure_port(exchange.HOST + ':' + str(exchange.PORT))
    server.start()
    exchange.sprint(f"Server initialized at {exchange.HOST} on port {exchange.PORT}")
    time.sleep(3)
    exchange.connect()
    exchange.heartbeat_thread.start()
    server.wait_for_termination()

def setup(num_servers: int, silent=False) -> List[multiprocessing.Process]:
    processes = []
    for i in range(num_servers):
        process = multiprocessing.Process(target=serve, args=(i, silent))
        processes.append(process)

    # Allow for ctrl-c exiting
    signal.signal(signal.SIGINT, sigint_handler)

    # Starts each process
    for process in processes:
        process.start()

    return processes

def main():
    # Allow for server creation by id through command-line args
    if len(sys.argv) == 2:
        try:
            machine_id = int(sys.argv[1])
            connection_wait_time = 5
            serve(machine_id)
        except KeyboardInterrupt:
            pass
    # Otherwise, spawn & connect servers using multiprocessing
    else:
        processes = []
    
        # Spawns a new process for each server that we have to run 
        setup(c.NUM_SERVERS)

if __name__ == '__main__':
    # Get your own hostname:
    hostname = socket.gethostbyname(socket.gethostname())
    print("Hostname:", hostname)
    main()
