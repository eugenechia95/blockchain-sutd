from hashlib import sha256
import time
import random
import sys

class Block:
  
  def __init__(self, previous_block, merkle_tree):
    self.transactions = merkle_tree
    self.header = {
      hash_previous: self.compute_hash(previous_block.header), 
      hash_merkle_root: self.compute_hash(merkle_tree.root), 
      timestamp: int(time.time()), 
      nonce: random.getrandbits(32)
    }

  @staticmethod
  def compute_hash(data):
    data = data.encode('utf-8')
    return sha256(data).hexdigest()
  
class Blockchain:

  MAX_BLOCK_SIZE = 1024 * 1024

  def __init__(self):
    self.chain = []
    self.target = random.getrandbits(32)
    self.temp_chain = []
  
  def add(block):
    if self.validate(block) == true:
      self.temp_chain.push(block)
      self.target = random.getrandbits(32)
      return true
    else:
      return false

  def validate(block):
    if Block.compute_hash(block.header) > self.target:
      return False
    if self.chain[-1].header.timestamp > block.header.timestamp:
      return False
    if sys.getsizeof(block) < Blockchain.MAX_BLOCK_SIZE:
      return False
    if Block.compute_hash(self.chain[-1].header) != block.header.hash_previous:
      return False
    return True

print(random.getrandbits(32))
