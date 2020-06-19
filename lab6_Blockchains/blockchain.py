import sys
from collections import deque
from datetime import datetime, timedelta
from itertools import count
from json import dumps, loads
from random import randint
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep

import merkletools as mlt
from Crypto.Hash import SHA256
from binascii import hexlify

# Based on: https://medium.com/coinmonks/implementing-blockchain-and-cryptocurrency-with-pow-consensus-algorithm-in-node-js-part-2-4524d0bf36a1
# Class that implements single block and mechanisms for mining it
class Block:
    # timestamp - time of block creation
    # lastHash  - hash value of last block
    # hash - current's block hash value
    # data - array of all previous transactions (blocks) hashes
    def __init__(self, timestamp, lastHash, hash, data, nonce):
        self.timestamp, self.lastHash, self.hash, self.data, self.nonce =\
            timestamp, lastHash, hash, data, nonce
    #

    # Generate block that will be the beginning of the blockchain
    @staticmethod
    def genesis():
        return Block('Genesis time', '', 'genesis hash', [], 0)

    @staticmethod
    def hash(timestamp, lastHash, data, nonce):
        return hexlify(SHA256.SHA256Hash(f"{timestamp}{lastHash}{data}{nonce}".encode()).digest()).decode()

    @staticmethod
    # Generate "mine" new block - this implements PoW (Proof-Of-Work) mechanism
    def mineBlock(lastBlock, data : "Series of hashes from transactions and a hash calculated from last block"):
        # Calculate hash of given transaction
        mt = mlt.MerkleTools(hash_type="sha256")
        mt.add_leaf(data, True)  # set the optional do_hash to true to have your value hashed prior to being added to the tree.
        mt.make_tree()

        # Calculated hash that needs to have Difficulty leading zeros
        lastHash = lastBlock.hash

        # Random value that will be incremented
        for nonce in count(0):
            timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            hash = Block.hash(timestamp, lastHash, mt.get_merkle_root(), nonce)
            # Check whether hash has required number of leading 0's
            if hash[:BlockChain.Difficulty].__eq__('0' * BlockChain.Difficulty):
                print(f"[*] New block! Difficulty: {BlockChain.Difficulty}, Nonce: {nonce}, New block: {Block(timestamp, lastHash, hash, data, nonce)}")
                return Block(timestamp, lastHash, hash, data, nonce)
    #

    @staticmethod
    def blockHash(block):
        return Block.hash(block.timestamp, block.lastHash, block.data, block.nonce)
    #

    # Change current difficulty based on time needed to mine a block
    def adjustDifficulty(self, lastBlock, timestamp):
        BlockChain.Difficulty = BlockChain.Difficulty if lastBlock.timestamp + timedelta(microseconds=BlockChain.MINE_RATE)\
            > timestamp else BlockChain.Difficulty - 1
    #

    def __str__(self):
        return f"{{{self.timestamp}{self.lastHash[:10]}-{self.hash[:10]}-{self.data}}}"
    #

    def toJSON(self):
        return dumps({'timestamp' : self.timestamp, 'lastHash' : self.lastHash, 'hash' : self.hash,
                      'data' : self.data, 'nonce' : self.nonce})

    @staticmethod
    def fromJSON(receivedBlock):
        receivedBlock = loads(receivedBlock)
        return Block(timestamp=receivedBlock['timestamp'], lastHash=receivedBlock['lastHash'],
                     hash=receivedBlock['hash'], data=receivedBlock['data'], nonce=receivedBlock['nonce'])

#

# Class that implements logic of creating chain of blocks, adding blocks and verifying them
class BlockChain:
    # Difficulty of PoW mechanism == number of leading zeros in a hash
    Difficulty = 5
    MINE_RATE  = 100

    # Create new chain of blocks
    def __init__(self, difficulty=Difficulty):
        BlockChain.Difficulty = difficulty
        self.chain = deque()
        self.chain.append(Block.genesis())
    #

    # Add new block to the chain
    def addBlock(self, data : "series of transactions"):
        block = Block.mineBlock(self.chain[-1], data)
        self.chain.append(block)
    #
    # Check whether this hash value already exists in chain
    # True - exists - you cannot add this block to the chain
    # False - does not exist - you can add it
    def checkBlock(self, recBlock):
        if recBlock.hash == self.chain[-1].hash:
            return True
        else:
            return False
    #

    # Validate chain against all its hashes
    def isValidChain(self, chain):
        if chain[0] != Block.genesis():
            return False

        for i in range(len(chain)):
            block = chain[i]
            lastBlock = chain[i - 1]

            if block.lastHash != lastBlock.hash or\
                block.hash != Block.blockHash(block):
                return False
        return True
    #

    # Replace currently stored chain with newly created by peers
    def replaceChain(self, newChain):
        if len(newChain) <= len(self.chain):
            print("Received chain is not longer than the current chain")
            return
        elif not self.isValidChain(newChain):
            print("Received chain is invalid")

        print("Replacing the current chain with new chain")
        self.chain = newChain
    #

    def getLastBlock(self):
        return self.chain[-1]
#

# Class that implements behaviour of P2P network
# Defines nodes behaviour, mining, sharing blocks, verifying them
class Miner:
    # Available modes:
    # 0 - Intermediate - does not mine, only shares information between nodes
    # 1 - Miner - does the dirty work
    def __init__(self, mode : "Default mode - miner" = 1, Difficulty=4,serverAddr : "server's ip & port that client (miner) connects to"=None):
        self.mode = mode
        self.serv = socket(AF_INET, SOCK_STREAM)

        # Start new chain
        self.blch = BlockChain(Difficulty)

        if self.mode == 0:
            self.intermediate()
        else:
            self.miner(serverAddr)

    # Main intermediate function
    def intermediate(self):
        # list of tuples of (address, port) to allow intermediate connect back to
        self.connected_clients = []
        defaultAddr = '0.0.0.0'
        PORT = randint(2500, 3500)
        try:
            self.serv.bind((defaultAddr, PORT))
        except OSError:
            PORT = randint(2500, 3500)
            self.serv.bind((defaultAddr, PORT))

        print(f"[*] Intermediate: Listening on {PORT}")
        self.serv.listen(4) # Allow 4 concurrent connections
        connection_nr = 1

        # Add thread that sends random hash every second
        def sender():
            while True:
                randomvalue = randint(0, 2 ** 30)
                newhash = hexlify(SHA256.SHA256Hash(f"{randomvalue}".encode()).digest())
                for client in self.connected_clients:
                    con = socket(AF_INET, SOCK_STREAM)
                    con.connect((client[0], int(client[1])))
                    con.send(newhash)
                sleep(1)
        #
        sthread = Thread(target=sender)

        def newBlockSenderFunction(data):
            recBlock = Block.fromJSON(data)
            # Check whether mined block already exist
            if not self.blch.checkBlock(recBlock):
                self.blch.chain.append(recBlock)
                print(f"[*] Verification complete. New block added. ")
                for client in self.connected_clients:
                    con = socket(AF_INET, SOCK_STREAM)
                    print(f"[*] Sending new block to ip: {client}")
                    con.connect((client[0], int(client[1])))
                    con.send(data.encode())
        #

        try:
            # Accept connection and add it to the list
            while True:
                conn, add = self.serv.accept()
                # When new client connects it will send port it's listening on for further instructions
                data = conn.recv(1024) # Size of received buffer
                if not data:
                    continue
                try:
                    data = int(data.decode())
                except ValueError:
                    print(f"[*] Client has mined a new block: {data.decode()}")
                    newBlockSender = Thread(target=newBlockSenderFunction, args=(data.decode(),))
                    newBlockSender.start()
                else:
                    self.connected_clients.append((add[0], data))
                    print(f"[*] New client with id {connection_nr} added (listening on port {data})")
                    connection_nr += 1
                    # Tell client it has been successfully added
                    conn.sendall(b'added')
                conn.close()

                # If anybody has connected
                if self.connected_clients and not sthread.is_alive():
                    sthread.start()

        except KeyboardInterrupt:
            print("[!] Server terminated by the user")
            exit(-1)
    #

    def miner(self, serverAddr : "Servers IP and port (tuple)"):
        print("[*] Starting miner execution")
        # global receivedHash ; global PORT; global defaultAddr
        PORT = randint(2500, 3500)
        defaultAddr = '0.0.0.0'
        self.receivedHash = None

        # This thread will receive hash every second from intermetiate
        def receiver():
            serv = socket(AF_INET, SOCK_STREAM)
            try:
                serv.bind((defaultAddr, PORT))
            except OSError:
                self.PORT = randint(2500, 3500)
                serv.bind((defaultAddr, PORT))

            print(f"[*] Client: Listening on {PORT} for information from intermediate")
            serv.listen(1)  # Allow 1 connection (from intermediate)

            while True:
                cl, ad = serv.accept()
                data = cl.recv(1024).decode().rstrip()
                if len(data) == 64:
                    self.receivedHash = data
                # If received new block
                elif "{" in data:
                    print("[*] Received mined block from intermediate. Restarting mining proces...")
                    self.minerthread.join()
                    self.minerthread = Thread(target=miner, args=(Block.fromJSON(data),))
                    self.minerthread.start()

                cl.close()
        #
        sthread = Thread(target=receiver)
        sthread.start()

        # Connect to intermediate
        tmpsock = socket(AF_INET, SOCK_STREAM)
        tmpsock.connect(serverAddr)
        # Send Client's listening port to the intermediate
        tmpsock.send(str(PORT).encode())
        # Receive information from server to confirm successful connection
        data = tmpsock.recv(1024).decode().rstrip()
        if data == 'added':
            print(f"[*] Succesfully connected to intermediate on port {serverAddr[1]}")
            tmpsock.close()
        else:
            print("[!] Connection failed. Exiting")
            exit()

        # This thread will do the actual mining
        def miner(block=None):
            print("[*] Waiting for transaction data from intermediate")
            if block is not None:
                print("[*] Mining new block based on data from intermediate")
                self.blch.addBlock([self.receivedHash])
                srv = socket(AF_INET, SOCK_STREAM)
                srv.connect(serverAddr)
                srv.send(self.blch.getLastBlock().toJSON().encode())

            try:
                while True:
                    # If client received hash from intermediate
                    if self.receivedHash:
                        print(f"[*] Received hash value from intermediate : {self.receivedHash}")
                        # Start new chain with default difficulty
                        self.blch.addBlock([self.receivedHash])
                        srv = socket(AF_INET, SOCK_STREAM)
                        srv.connect(serverAddr)
                        srv.send(self.blch.getLastBlock().toJSON().encode())

                    sleep(1)
            except KeyboardInterrupt:
                print("[!] Client terminated by the user")
                exit(-1)
        #

        self.minerthread = Thread(target=miner, args=(None,))
        self.minerthread.start()

        while True:
            pass
    #
#

def test():
    blch = BlockChain(6) # Difficulty == 4
    starttime = datetime.now()
    blch.addBlock([]) # Add empty transaction's hashes list
    endtime = datetime.now()
    print(f"Mining took: {(endtime - starttime).seconds} seconds")

if __name__ == '__main__':
    Difficulty = 5 # number of leading 0's for PoW

    if len(sys.argv) == 1:
        print(f"""
BlockChain PoW simulation. Usage: 
    (Start miner worker)
    python {sys.argv[0]} client <target_ip> <target_port>
        * <target_ip>         IP of the server (intermediate)
        * <target_port>       Port that the server is listening on
    
    (Start intermediate server that shares results of mining)
    python {sys.argv[0]} server
        """)
        exit(-1)

    if len(sys.argv) == 2:
        if sys.argv[1] == 'server':
            m = Miner(0, Difficulty=Difficulty)
        else:
            print("[!] Wrong arguments! Exiting.")
            exit()

    if len(sys.argv) == 4:
        if sys.argv[1] == 'client':
            try:
                m = Miner(Difficulty=Difficulty,serverAddr=(sys.argv[2], int(sys.argv[3])))
            except ValueError:
                print("[!] Port must be a number!")
                exit()
#


