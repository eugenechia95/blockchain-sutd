from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey, NIST384p
import json
import time
import copy
from q5 import *
from q4 import *


class Block:
    def __init__(self, index, transactions, previous_hash):
        """
        Constructor for the `Block` class.
        :param index:         Unique ID of the block.
        :param transactions:  Merkle Tree.
        :param timestamp:     Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of.                                        
        """
        self.index = index
        self.transactions = transactions
        self.header = {
            "previous_hash": previous_hash, # Adding the previous hash field
            "hash_merkle_root": self.compute_hash(transactions.root) if transactions != [] else None, 
            "timestamp": int(time.time()), 
            "nonce": 0
        }
        self.block = ""

    @staticmethod
    def compute_hash(data):
        """
        Returns the hash of the block instance by first converting it
        into JSON string.
        """
        data = bytes(data)
        data = data.encode('utf-8')
        return sha256(data).hexdigest()

class Blockchain:

    # difficulty of PoW algorithm
    TARGET = 2

    #reward for mining blocks
    REWARD = 100

    def __init__(self):
        """
        Constructor for the `Blockchain` class.
        """
        self.unconfirmed_transactions = [] # data yet to get into blockchain
        self.chain = []
        self.forked_chains = {}
        self.create_genesis_block()

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], "0")
        genesis_block.hash = Block.compute_hash(genesis_block.header)
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """
        A quick pythonic way to retrieve the most recent block in the chain. Note that
        the chain will always consist of at least one block (i.e., genesis block)
        """
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Function that tries different values of the nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.header["nonce"] = 0

        computed_hash = Block.compute_hash(block.header)
        while not computed_hash.startswith('0' * Blockchain.TARGET):
            block.header["nonce"] += 1
            computed_hash = Block.compute_hash(block.header)

        return computed_hash

    def add_block(self, block, proof, target_fork="main", new_fork=None, index=None):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of a latest block
          in the chain match.
        Miners can choose which fork to add to. 
        If new_fork name is specified, create new fork based on existing targeted fork chain and index and add to new fork chain
        If no new fork_name is specified,
            block adds to the targeted chain. Default chain is the main chain.
        Index only matters for new fork creation
        If last 3 arguments not supplied, add block to main chain
        """

        selected_fork = self.chain if target_fork == "main" else self.forked_chains[target_fork]
        if new_fork == None:
            selected_chain = selected_fork
        else:
            index = len(selected_fork) if index == None else index
            self.forked_chains[new_fork] = copy.copy(selected_fork[0:index+1])
            selected_chain = self.forked_chains[new_fork]

        previous_hash = self.last_block.hash

        if previous_hash != block.header["previous_hash"]:
            return False

        if not self.validate(block, proof):
            return False

        block.hash = proof
        selected_chain.append(block)
        
        return True

    def validate(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.TARGET) and
                block_hash == Block.compute_hash(block.header))

    def resolve(self):
        longest_chain = self.chain
        for i in self.forked_chains.values():
            if len(i) == len(longest_chain):
                raise Exception("Two chains with similar length!")
            if len(i) > len(longest_chain):
                longest_chain = i
        self.chain = longest_chain
        return self.last_block

class Miner:

    def __init__(self):
        """
        Constructor for the `Miner` class.
        """
        self.coins = 0

    def mine(self, blockchain, target_fork="main", new_fork=None, index=None):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out proof of work.
        """
        if not blockchain.unconfirmed_transactions:
            return False

        selected_transaction = blockchain.unconfirmed_transactions[0]
        last_block = blockchain.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=selected_transaction,
                          previous_hash=last_block.hash)

        proof = blockchain.proof_of_work(new_block)
        blockchain.add_block(new_block, proof, target_fork, new_fork, index)
        blockchain.unconfirmed_transactions.pop(0)

        self.add_coins(blockchain.REWARD)
        return new_block.index

    def add_coins(self, amount):
        self.coins += amount

# data_chunks = ["test", "testing", "testing1", "testing2"]
sk = SigningKey.generate(curve=NIST384p)
vk = sk.verifying_key
tx = Transaction(vk, vk, "5", "5")
data_chunks = [tx, tx, tx, tx]
mk = MerkleTree(data_chunks)
blockchain = Blockchain()
print(blockchain.chain)
blockchain.add_new_transaction(mk)
blockchain.add_new_transaction(mk)
blockchain.add_new_transaction(mk)
blockchain.add_new_transaction(mk)
miner = Miner()
miner.mine(blockchain)
miner.mine(blockchain)
miner.mine(blockchain, "main", "newchain")
miner.mine(blockchain, "newchain", "newerchain", 1)
print(blockchain.forked_chains)
print(blockchain.chain)
print(miner.coins)
blockchain.resolve()
print(blockchain.chain)
