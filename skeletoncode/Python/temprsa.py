import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
import time
import sys
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)  # generate pub and priv key

publickey = key.publickey()  # pub key export for exchange

#print('=' * 100)
plain_text = sys.argv[3]
with open(plain_text,'r') as f:
    plain_text = f.read()
#print("Plaintext is: ", plain_text)
# print
before_time = time.time()

cipher_text = publickey.encrypt(plain_text, 32)
current_time = time.time()

print("encrytime is costs (milliseconds)",(current_time-before_time)*1000)
# message to encrypt is in the above line 'encrypt this message'
#print('Plaintext encrypted using Public Key is:', cipher_text)
# print
# decrypted code below
before_time = time.time()

decrypted = key.decrypt(ast.literal_eval(str(cipher_text)))
current_time = time.time()

print("decrytime is costs (milliseconds)",(current_time-before_time)*1000)
#print('Ciphertext decrypted with Private key is', decrypted)
#print('=' * 100)
