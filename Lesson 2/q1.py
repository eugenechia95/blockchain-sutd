from ecdsa import SigningKey, NIST384p
from json import JSONEncoder
import json

class Transaction:
  
  def __init__(self, sender, receiver, amount, comment, signature):
    # Instantiates object from passed values
    self.sender = sender
    self.receiver = receiver
    self.amount = amount
    self.comment = comment
    self.signature = signature

  def serialize(self):
    # Serializes object to CBOR or JSON string
    return json.dumps(self, default=lambda obj: obj.__dict__)


  @classmethod
  def deserialize(cls, json_data):
    # Instantiates/Deserializes object from CBOR or JSON string
    deserialized = json.loads(json_data)
    Transaction(deserialized["sender"], deserialized["receiver"], deserialized["amount"], deserialized["comment"], deserialized["signature"])
    return deserialized



  def sign(private_key):
    # Sign object with private key passed
    # That can be called within new()
    signature = sk.sign(bytes(self))
    return signature



  def validate(signature):
    # Validate transaction correctness.
    # Can be called within from_json()
    assert vk.verify(signature, bytes(self))

  # def __eq__(...):
  #   # Check whether transactions are the same

tx = Transaction("5", "5", "5", "5", "5")
print(tx.sender)
y = tx.serialize()
z = Transaction.deserialize(y)
print(y)
print(z)
