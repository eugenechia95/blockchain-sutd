import hashlib

input = ("Blockchain Technology").encode('utf-8')
m_sha2256 = hashlib.sha256()
m_sha2256.update(input)
output_sha2256 = m_sha2256.digest()
print(output_sha2256)

m_sha2512 = hashlib.sha512()
m_sha2512.update(input)
output_sha2512 = m_sha2512.digest()
print(output_sha2512)

m_sha3256 = hashlib.sha3_256()
m_sha3256.update(input)
output_sha3256 = m_sha3256.digest()
print(output_sha3256)

m_sha3512 = hashlib.sha3_512()
m_sha3512.update(input)
output_sha3512 = m_sha3512.digest()
print(output_sha3512)
