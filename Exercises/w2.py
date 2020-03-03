from hashlib import sha256
import json
import time
from q5 import *


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
    difficulty = 2

    def __init__(self):
        """
        Constructor for the `Blockchain` class.
        """
        self.chain = []
        self.forked_chains = []
        self.create_genesis_block()

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
        block.nonce = 0

        computed_hash = Block.compute_hash(block.header)
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = Block.compute_hash(block.header)

        return computed_hash

    def add_block(self, block, proof, fork, index):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of a latest block
          in the chain match.
        """
        if fork == true:
            selected_chain = (self.chain[0:index+1].copy())
        else:
            selected_chain = self.chain


        previous_hash = self.last_block.hash

        if previous_hash != block.header["previous_hash"]:
            return False

        if not Blockchain.validate(block, proof):
            return False

        block.hash = proof
        selected_chain.append(block)
        self.forked_chains.append(selected_chain)
        return True

    def validate(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == Block.compute_hash(block.header))

    def resolve(self):
        longest_chain = self.chain
        for i in self.forked_chains:
            if len(i) > len(longest_chain):
                longest_chain = i
        self.chain = longest_chain
        return longest_chain.last_block

data_chunks = ["test", "testing", "testing1", "testing2"]
mk = MerkleTree(data_chunks)
blockchain = Blockchain()
new_block = Block(1, mk, "0")
proof = Block.compute_hash(new_block.header)
print(blockchain.add_block(new_block, proof, fork, false, None))
