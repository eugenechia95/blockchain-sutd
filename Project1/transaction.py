from ecdsa import SigningKey, VerifyingKey, NIST384p
from json import JSONEncoder
import copy
import json
import base64

# Assumption: 1 sender, 1 receiver
class Transaction:
  
  def __init__(self, sender, receiver, amount, comment):
    """
    Constructor for the `Transaction` class.
    :param sender: public address of sender
    :param receiver:  public address of receiver
    :param amount: amount of money to transfer
    :param comment: additional comments                                     
    """
    self.sender = sender
    self.receiver = receiver
    self.amount = amount
    self.comment = comment
    self.signature = ""

  def reprJSON(self):
    return dict(sender = self.sender, receiver=self.receiver, amount=self.amount, comment=self.comment)

  def serialize(self):
    # Serializes object to CBOR or JSON string
    return json.dumps(self, default=lambda obj: obj.__dict__)

  @classmethod
  def deserialize(cls, json_data):
    # Instantiates/Deserializes object from CBOR or JSON string
    deserialized = json.loads(json_data)
    new_transaction = Transaction(deserialized["sender"], deserialized["receiver"], deserialized["amount"], deserialized["comment"])
    return new_transaction

  def sign(self, private_key):
    # Sign object with private key passed
    # That can be called within new()
    s = self.serialize()
    signature = private_key.sign(s)
    self.signature = signature

  def validate(self):
    # Validate transaction correctness.
    # Can be called within from_json()
    tmp = self.signature

    duplicated_object = copy.deepcopy(self)
    duplicated_object.signature = ""
    s = duplicated_object.serialize()
    decoded_public_key = base64.decodestring(duplicated_object.sender)
    public_key = VerifyingKey.from_string(decoded_public_key, curve=NIST384p)
    assert public_key.verify(tmp, s)

  @classmethod
  def __eq__(cls, transaction_1, transaction_2):
    # Check whether transactions are the same
    copy_1 = copy.deepcopy(transaction_1)
    copy_2 = copy.deepcopy(transaction_2)
    copy_1.signature = ""
    copy_2.signature = ""
    if copy_1.serialize() == copy_2.serialize():
      return True
    else:
      return False

# sk = SigningKey.generate(curve=NIST384p)
# vk = sk.verifying_key

# tx = Transaction(vk, vk, "5", "5")
# y = tx.serialize()
# tx.sign(sk)
# tx.validate()
# tx2 = copy.deepcopy(tx)
# outcome = Transaction.__eq__(tx, tx2)
# print(outcome)
