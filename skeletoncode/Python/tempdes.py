from encodings import utf_8
from Crypto.Cipher import DES
import sys
import time



def isvalid(str):
    for item in str:
        if not ('0' <= item <= '9' or 'a' <= item < 'g' or 'A' <= item < 'G'):
            return False
    return True
try:
    if not isvalid(sys.argv[1]):
        raise ValueError
except ValueError:
    print("Error: iv is not comprised only of hexadecimal digits")
    sys.exit()
try:
    if not isvalid(sys.argv[2]):
        raise ValueError
except ValueError:
    print("Error: the key is not comprised only of hexadecimal digits")
    sys.exit()
try:
    iv = bytearray.fromhex(sys.argv[1])
    if len(iv) != 8:
        raise ValueError
except ValueError:
    print("Error:length of iv isn't right")
    sys.exit()
try:
    cbc_key = bytearray.fromhex(sys.argv[2])
    if len(cbc_key) != 8:
        raise ValueError
except ValueError:
    print("Error:length of the key isn't right")
    sys.exit()

des1 = DES.new(cbc_key, DES.MODE_CBC, iv)
des2 = DES.new(cbc_key, DES.MODE_CBC, iv)

with open(sys.argv[3]) as f:
    plain_text = f.read()
plain_text = plain_text.encode('utf-8').decode('latin-1')

pad = 8 - len(plain_text) % 8
if pad != 8:
    plain_text = plain_text + ' ' * pad

start1 = time.time()
cipher_text = des1.encrypt(plain_text.encode("latin-1"))

end1 = time.time()
print("The encrypt time (milliseconds) is", (end1 - start1) * 1000000)
with open(sys.argv[4], 'a', encoding='latin-1') as f1:
    f1.write(cipher_text.decode("latin-1"))
print(cipher_text.decode("latin-1").encode("utf-8"))
start2 = time.time() 
msg = des2.decrypt(cipher_text)
print(msg)
end2 = time.time()
print("The decrypt time (milliseconds) is ", (end2 - start2) * 1000000)