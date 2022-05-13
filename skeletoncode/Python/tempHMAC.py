#Following code reads its source file and computes an HMAC signature for it:
import hmac
import sys
import time

secret_key = bytearray.fromhex(sys.argv[2])*2
digest_maker = hmac.new(secret_key,None,digestmod="sha1")#in your code replace key

f = open(sys.argv[3], 'rb')
before_time = time.time()
try:
    while True:
        block = f.read(1024)
        if not block:
            break
        digest_maker.update(block)
finally:
    f.close()

digest = digest_maker.hexdigest()
current_time = time.time()

print("time is costs (milliseconds)",(current_time-before_time)*1000000)

"""print('='*100)
print("HMAC digest generated for \"lorem.txt\" file is:", digest)
print('='*100)"""
