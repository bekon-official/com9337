from asyncio.windows_events import NULL
import socket
import time
import random
from threading import Thread
from decimal import Decimal
import re
from binascii import unhexlify
from hashlib import md5
from ecdsa import SECP128r1, SigningKey, ECDH
from Crypto.Protocol.SecretSharing import Shamir
from pybloom_live import BloomFilter
import pickle
import os

shares = []
received_shares = {}
received_EphID = []
secret_hash = NULL
hash_send = NULL
EphID = NULL
ownEphID = 0
ownEphIDList=[]
negative_people = True
positive_and_proved_people = False
bloom = BloomFilter(capacity=3200)
qbf = BloomFilter(capacity=3200)
udpserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
# Enable broadcasting mode
udpserver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udpserver.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)

udpserver.bind(('', 80))
_ten = Decimal('10')
FIELD_SIZE = 10 ** 5


def make_key():
    secexp = random.randrange(10000000000000000000000000000000000000, 99999999999999999999999999999999999999)
    return SigningKey.from_secret_exponent(secexp, curve=SECP128r1)


def reconstruct_secret(shares):

    return Shamir.combine(shares)


def generate_shares(secret, secret_hash):
    """
    Split given `secret` into `n` shares with minimum threshold
    of `m` shares to recover this `secret`, using SSS algorithm.
    """
    count = 0
    shares = Shamir.split(3, 5, secret)
    print(f'Segment 2: 5 Shares generation DONE. Shares: {", ".join(str(share) for share in shares)}')
    # print(shares)
    for share in shares:

        count = count + 1
        x = random.random()
        hash_send = str(secret_hash)
        ownEphIDList.append(hash_send)

        if (x >= 0.5):
            print("Segment 3-A: send a share:", str(share) + "@" + hash_send)
            udpserver.sendto((str(share) + "@" + hash_send).encode('utf8'), ('<broadcast>', 80))
        if (count == 5):
            udpserver.sendto((hash_send + "@end sending").encode('utf8'), ('<broadcast>', 80))
        time.sleep(3)

    return shares


def generate_share():
    while True:
        sk = make_key()
        s = sk.to_string()  # bytes，size of .hex（）is 32
        global ownEphID
        ownEphID = sk

        print("Segment 1: EphID generation DONE. EphID:" + str(s.hex()))
        # print("hash:"+str(md5(unhexlify(int(s))).hexdigest()))
        secret_hash = md5(unhexlify(str(s.hex()).encode())).hexdigest()
        shares = generate_shares(int.from_bytes(s, "big"), secret_hash)




def receive_share():
    # Look for the response
    while True:
        data = udpserver.recv(1024).decode()
        matchEnd = re.match(r'^(.*)@end sending$', data, re.M | re.I)
        matchObj = re.match(r'^(.*)@(.*)$', data, re.M | re.I)
        #print('received:',data)
        # print(type(data))
        if (matchEnd and (str(matchEnd.group(1)) not in ownEphIDList)):
            if (matchEnd.group(1) in received_shares):
                print('Segment 3-B: Received a share')
                print("Segment 3-C: Number of shares it receive is ", str(len(received_shares[matchEnd.group(1)])))
                if (len(received_shares[matchEnd.group(1)]) > 2):
                    EphID = reconstruct_secret(received_shares[matchEnd.group(1)][0:3])
                    result_hash = md5(unhexlify(str(EphID.hex()).encode())).hexdigest()
                    print("Segment 4-A: EphID reconstruction DONE. EphID hash: ", result_hash, "hash received is ",
                          matchEnd.group(1))
                    if (str(result_hash) == matchEnd.group(1)):
                        print("Segment 4-B:EphID reconstructed is verified")
                        received_EphID.append(str(EphID))
                        global ownEphID
                        ecdh = ECDH(curve=SECP128r1, private_key=ownEphID,
                                    public_key=SigningKey.from_string(EphID, SECP128r1).verifying_key)
                        EncID = ecdh.generate_sharedsecret_bytes()
                        # print("Segment 5-A: GET ownEnpID:" + str(ownEphID.to_string().hex()))
                        print("Segment 5-A: GET EncID:" + str(EncID.hex()))
                        print("Segment 7-A:The length of DBF is ", len(bloom))
                        bloom.add(EncID)
                        qbf.add(EncID)
                        print("Segment 6:Add EncID to DBF and delete the EncID")
                        print("Segment 7-A:Now the length of DBF is ", len(bloom))
                        del EncID
                    else:
                        print("EphID is not right, we will try again")
                # print(received_shares[matchEnd.group(1)])
                del received_shares[matchEnd.group(1)]
        elif ((not matchEnd) and matchObj and (str(matchObj.group(2)) not in ownEphIDList)):
            try:
                res = eval(matchObj.group(1))
            except:
                os._exit(0)
            if (matchObj.group(2) not in received_shares):
                received_shares[str(matchObj.group(2))] = [res]
            else:
                list = received_shares[matchObj.group(2)]
                list.append(res)
                received_shares[matchObj.group(2)] = list


def manageDBF():
    while True:
        global qbf

        bloomold = BloomFilter(capacity=3200)  # QBF
        #print("QBF bitarray length before combine:", bloomold.bitarray.count())
        for i in range(6):
            global bloom

            print("Segment 7-B: A new DBF has been created from 3 encounters.")
            bloom = BloomFilter(capacity=3200)


            time.sleep(90)
            # reference https://stackoverflow.com/questions/55447437/how-can-i-get-the-size-of-bloom-filter-set-while-using-union-or-intersection-fun
            bloomold = bloom.union(bloomold)
        #print("QBF bitarray length after combine:", bloomold.bitarray.count())

        ## send QBF to server below
        global negative_people
        global positive_and_proved_people
        while (negative_people):

            global answer
            print("Segment 8: DBFs have combined into QBF")
            data_string = pickle.dumps(qbf)
            sock.send(data_string)
            qbf = BloomFilter(capacity=3200)

            print("Segment 9:QBF have been sent to back-end server")

            data = sock.recv(1024).decode()
            if (data == 'You are diagnosed positive'):
                print("Segement 10-B:", data)
                data = sock.recv(1024).decode()
                print("Segement 10-B:", data)
                if (data == 'Update success'):
                    negative_people = False
                    positive_and_proved_people = True
                    time.sleep(540)
                elif (data == "You reject sending"):
                    negative_people = False
            else:
                print(data)
            break

        while (positive_and_proved_people):
            print(qbf.bitarray.count())
            data_string = pickle.dumps(qbf)
            sock.send(data_string)
            qbf = BloomFilter(capacity=3200)
            data = sock.recv(1024).decode()
            print("Segement 10-B:", data)
            break


if __name__ == '__main__':
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.bind(('', 80))
    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)

    # print('connecting to %s port %s' % server_address, file=sys.stderr)
    print("If you are diagnosed positive, willing to send your connect data? (type Y/N, Y in default)")
    print("You can change anytime you want")
    answer = 'Y'
    try:
        sock.connect(server_address)
        data = sock.recv(1024).decode()
    except Exception as e:
        print(e)
    thread = Thread(target=generate_share)
    thread.setDaemon(True)
    thread.start()
    thread = Thread(target=receive_share)
    thread.setDaemon(True)
    thread.start()
    thread = Thread(target=manageDBF)
    thread.setDaemon(True)
    thread.start()
    while True:
        answer = input()
        sock.send(answer.encode())
        print("update you choice:", answer)
