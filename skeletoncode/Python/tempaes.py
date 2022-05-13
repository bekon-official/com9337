from Crypto.Cipher import AES
from Crypto import Random
import sys
import time
"""this one can be random"""
cbc_key = bytearray.fromhex(sys.argv[2])*2
""" print('=' * 100)
print('Key used: ', [x for x in cbc_key]) """

iv = bytearray.fromhex(sys.argv[1])*2
""" print("IV used: ", [x for x in iv])
print('=' * 100) """
aes1 = AES.new(cbc_key, AES.MODE_CBC, iv)
aes2 = AES.new(cbc_key, AES.MODE_CBC, iv)


plain_text = sys.argv[3]
with open(plain_text,'r') as f:
    plain_text = f.read()
before_time = time.time()

cipher_text = aes1.encrypt(plain_text.encode("latin-1"))
""" print("Ciphertext is: ", cipher_text) """

msg = aes2.decrypt(cipher_text)
current_time = time.time()

""" print("Decrypted message: ", msg)
print('=' * 100) """

print("time is costs (milliseconds)",(current_time-before_time)*1000)