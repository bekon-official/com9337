import hashlib
import sys
import time
#initializing string


with open(sys.argv[3],'r') as f:
    plain_text = f.read()
"""print('='*100)"""
before_time = time.time()  

result = hashlib.sha1(plain_text.encode()) 
  
# printing the equivalent hexadecimal value. 
"""print("The hexadecimal equivalent of SHA1 digest is : ") 
print(result.hexdigest())
print('='*100)"""
current_time = time.time()
print("time is costs (milliseconds)",(current_time-before_time)*1000000)