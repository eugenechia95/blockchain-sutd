from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey, NIST384p
import json
import time
import copy
import base64
from merkle import *
from transaction import *


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
    TARGET = 5

    # reward for mining blocks
    REWARD = 100

    # number of blocks to be mined before reward is released
    LOCKTIME = 6

    def __init__(self):
        """
        Constructor for the `Blockchain` class.
        """
        # coins attribute is a dictionary of miner public keys and the amount of coins they have
        self.unconfirmed_transactions = [] # data yet to get into blockchain
        self.locked_coins = [] # blocks are coined but yet to release coins until LOCKTIME over
        self.chain = []
        self.forked_chains = {}
        self.create_genesis_block()
        self.coins = {}

    # Add merkle tree made up on many transactions here
    def add_new_transaction(self, merkle_tree):
        self.validate_transaction(merkle_tree)
        self.unconfirmed_transactions.append(merkle_tree)

    def validate_transaction(self, merkle_tree):
        for i in merkle_tree.leaves:
            transaction = i.data
            # checks if transaction public key can verify transaction
            result = transaction.validate()
            # checks if transaction amount is less than sender's coin balance
            decoded_sender_public_key = base64.decodestring(transaction.sender)
            sender_public_key = str(VerifyingKey.from_string(decoded_sender_public_key, curve=NIST384p))
            decoded_receiver_public_key = base64.decodestring(transaction.receiver)
            receiver_public_key = str(VerifyingKey.from_string(decoded_receiver_public_key, curve=NIST384p))
            amount = transaction.amount
            if (self.coins.get(sender_public_key) == None):
                self.coins[(sender_public_key)] = 0
            if (self.coins.get(receiver_public_key) == None):
                self.coins[(receiver_public_key)] = 0
            if amount > self.coins[(sender_public_key)]:
                raise Exception("Transaction amount is more than amount of coins sender has")

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

    # Method used by miner nodes to sync blockchains from other notes
    def quick_add_block(self, block, proof, target_fork="main"):
        
        selected_fork = self.chain if target_fork == "main" else self.forked_chains[target_fork]

        previous_hash = self.last_block.hash

        if previous_hash != block.header["previous_hash"]:
            return False

        if not self.validate(block, proof):
            return False

        block.hash = proof
        selected_chain.append(block)
        
        return True

    def add_block(self, miner, block, proof, target_fork="main", new_fork=None, index=None):
        """
        A function called by miner that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.print(blockchain.coins)
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

        self.add_transacted_coins(block, miner)
        self.release_locked_coins()
        
        return True

    def validate(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.TARGET) and
                block_hash == Block.compute_hash(block.header))

    # Coins are added to locked_coins of blockchain which are released only after locktime
    def add_transacted_coins(self, block, miner):

        block_locked_coins = {}

        # Add miner's reward to block's locked_coins
        encoded_miner_coins_key = base64.encodestring(miner.public_key.to_string())
        decoded_miner_coins_key = base64.decodestring(encoded_miner_coins_key)
        miner_coins_key = str(VerifyingKey.from_string(decoded_miner_coins_key, curve=NIST384p))
        if (block_locked_coins.get(miner_coins_key) == None):
                block_locked_coins[(miner_coins_key)] = 0
        block_locked_coins[miner_coins_key] += blockchain.REWARD

        for i in block.transactions.leaves:
            transaction = i.data
            # checks if transaction public key can verify transaction
            result = transaction.validate()
            # checks if transaction amount is less than sender's coin balance
            decoded_sender_public_key = base64.decodestring(transaction.sender)
            sender_public_key = str(VerifyingKey.from_string(decoded_sender_public_key, curve=NIST384p))
            decoded_receiver_public_key = base64.decodestring(transaction.receiver)
            receiver_public_key = str(VerifyingKey.from_string(decoded_receiver_public_key, curve=NIST384p))
            amount = transaction.amount
            if (block_locked_coins.get(sender_public_key) == None):
                block_locked_coins[(sender_public_key)] = 0
            if (block_locked_coins.get(receiver_public_key) == None):
                block_locked_coins[(receiver_public_key)] = 0

            block_locked_coins[sender_public_key] += -1 * amount
            block_locked_coins[receiver_public_key] += amount

            
        # Adds block's locked_coins to blockchain's locked_coin_array
        blockchain.locked_coins.append(block_locked_coins)

    # Release locked coins after LOCKTIME into spendable coins
    def release_locked_coins(self):
        if len(self.locked_coins) > Blockchain.LOCKTIME:
            locked_coins = self.locked_coins.pop(0)
            for i in locked_coins.keys():
                self.coins[i] += locked_coins[i]

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

    def __init__(self, public_key):
        """
        Constructor for the `Miner` class.
        """
        self.public_key = public_key

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
        blockchain.add_block(self, new_block, proof, target_fork, new_fork, index)
        blockchain.unconfirmed_transactions.pop(0)
        print("Block mined!")
        return new_block.index
    
    def get_coins(self, blockchain):
        encoded_miner_coins_key = base64.encodestring(self.public_key.to_string())
        decoded_miner_coins_key = base64.decodestring(encoded_miner_coins_key)
        miner_coins_key = str(VerifyingKey.from_string(decoded_miner_coins_key, curve=NIST384p))
        if (blockchain.coins.get(miner_coins_key) == None):
            raise Exception("Miner has no coins")
        return blockchain.coins[miner_coins_key]

# sk = SigningKey.generate(curve=NIST384p)
# vk = sk.verifying_key

# miner_a_private_key = SigningKey.generate(curve=NIST384p)
# miner_a_public_key = miner_a_private_key.verifying_key
# miner_b_private_key = SigningKey.generate(curve=NIST384p)
# miner_b_public_key = miner_b_private_key.verifying_key
# valueless_tx = Transaction(miner_a_public_key, miner_b_public_key, 0, "")
# normal_tx = Transaction(miner_a_public_key, miner_b_public_key, 5, "")
# valueless_tx.sign(miner_a_private_key)
# normal_tx.sign(miner_a_private_key)
# valueless_mk = MerkleTree([valueless_tx])
# normal_mk = MerkleTree([normal_tx, normal_tx, normal_tx])
# blockchain = Blockchain()
# print(blockchain.chain)
# blockchain.add_new_transaction(valueless_mk)
# blockchain.add_new_transaction(valueless_mk)
# miner_a = Miner(miner_a_public_key)
# miner_b = Miner(miner_b_public_key)
# miner_a.mine(blockchain)
# miner_a.mine(blockchain)

# i=0
# j=0
# while (i<10):
#    blockchain.add_new_transaction(mk)
#    i+=1
# while (j<10):
#     miner.mine(blockchain)
#     print(int(time.time()))
#     j+=1

