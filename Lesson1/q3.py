from ecdsa import SigningKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
vk = sk.verifying_key
signature = sk.sign(b"Blockchain Technology")
print(signature)
assert vk.verify(signature, b"Blockchain Technology")
