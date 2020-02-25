from hashlib import sha256
import time
import random
import sys
from q5 import *

class Block:
  
  def __init__(self, previous_block, merkle_tree):
    self.transactions = merkle_tree
    self.header = {
      "hash_previous": self.compute_hash(previous_block.header) if previous_block else None, 
      "hash_merkle_root": self.compute_hash(merkle_tree.root), 
      "timestamp": int(time.time()), 
      "nonce": random.getrandbits(32)
    }

  @staticmethod
  def compute_hash(data):
    data = bytes(data)
    data = data.encode('utf-8')
    return sha256(data).hexdigest()
  
class Blockchain:

  MAX_BLOCK_SIZE = 1024 * 1024

  def __init__(self):
    self.chain = []
    self.target = random.getrandbits(128)
    self.temp_chain = []
  
  def add(self, block):
    if self.validate(block) == True:
      print("passed")
      self.temp_chain.append(block)
      self.target = random.getrandbits(128)
      return True
    else:
      return False

  def validate(self, block):
    # if Block.compute_hash(block.header) > self.target:
    #   print("failed")
    #   return False
    # if sys.getsizeof(block) < Blockchain.MAX_BLOCK_SIZE:
    #   return False
    if len(self.chain) == 0:
      return True
    if self.chain[-1].header.timestamp > block.header.timestamp:
      return False
    if block.header.hash_previous and Block.compute_hash(self.chain[-1].header) != block.header.hash_previous:
      return False
    return True

data_chunks = ["test", "testing", "testing1", "testing2"]
mk = MerkleTree(data_chunks)
first_block = Block(None, mk)
second_block = Block(first_block, mk)
blockchain = Blockchain()
blockchain.add(first_block)
blockchain.add(second_block)
print(blockchain.target)
print(Block.compute_hash(first_block.header))
