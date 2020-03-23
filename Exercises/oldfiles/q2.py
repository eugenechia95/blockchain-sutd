import hashlib
import datetime
import random
import string

class Collision:
  @staticmethod
  def randomString():
    stringLength = 10
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

  @classmethod
  def H(cls, n, msg):
    m_sha2512 = hashlib.sha512()
    m_sha2512.update(msg.encode('utf-8'))
    output = m_sha2512.digest()
    # print(output[:n])
    return output[:n]

  @classmethod
  def find_match(cls, n):
    match = False
    T1 = datetime.datetime.now()
    hash_table = {}
    while match == False:
      msg = cls.randomString()
      new_output = cls.H(n, msg)
      if new_output in hash_table:
        match = True
      else:
        hash_table[new_output] = True
    T2 = datetime.datetime.now()
    time_taken = T2 - T1
    print(time_taken)

  @classmethod
  def run_match(cls):
    i = 1
    while i < 6:
      print("H(%d, msg)" %(i))
      cls.find_match(i)
      i += 1

class PreImage:

  @classmethod
  def find_match(cls, hash, n):
    match = False
    T1 = datetime.datetime.now()
    while match == False:
      msg = Collision.randomString()
      new_output = Collision.H(n, msg)
      if new_output == hash:
        match = True
    T2 = datetime.datetime.now()
    time_taken = T2 - T1
    print(msg)
    print(time_taken)

  @classmethod
  def run_match(cls):
    hashes = [b'\x00', b'\x00'*2, b'\x00'*3, b'\x00'*4, b'\x00'*5]
    i = 1
    while i < 6:
      hash = hashes[i-1]
      print("H(%d, %s)" %(i, hash))
      cls.find_match(hash, i)
      i += 1

Collision.run_match()
# PreImage.run_match()

# Collision Run Times:
# H(1, msg)
# 0:00:00.000072
# H(2, msg)
# 0:00:00.001269
# H(3, msg)
# 0:00:00.023033
# H(4, msg)
# 0:00:00.294031
# H(5, msg)
# 0:00:12.651310

# Pre Image Run Times:
# H(1, b'\x00')
# mbkqmoliio
# 0:00:00.002238
# H(2, b'\x00\x00')
# pbswzjalgg
# 0:00:00.612449
# H(3, b'\x00\x00\x00')
# tftqizvqce
# 0:01:13.391936

