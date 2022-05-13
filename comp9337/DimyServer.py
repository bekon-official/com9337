from asyncio.windows_events import NULL
import socket
import sys
from threading import Thread
import threading 
import pickle
from pybloom_live import BloomFilter

g_socket_server = None 
g_conn_pool = {}
CBF_list = BloomFilter(capacity=3200)

# a dict 1 means people is safe and willing to send data, 2 means not want to send data, 
# 3 means positive and willing to send data 
people = {'x': 1, 'y': 2}

# Create a TCP/IP socket
g_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print('starting up to %s port %s' % server_address, file=sys.stderr)
g_socket_server.bind(server_address)
g_socket_server.listen(5)  
print("server start, wait for client connecting...")
count=0
def accept_client(client, client_address):
    global people
    while True:
        try:
            print(client,client_address)
            people[client_address]=1
            thread = Thread(target=message_handle, args=(client, client_address))
            thread.setDaemon(True)
            thread.start()
            client.sendall("connect server successfully!".encode(encoding='utf8'))
            message_handle(client, client_address)
        except Exception as e:
            print(e)
            remove_client(client_address)
            break

def message_handle(client, client_address):
    global people
    while True:
        try:
            data, addr = client.recvfrom(102400)
            if(len(data)<5000):
                if((str(data.decode()) not in ['Y','Yes','yes','y'])):
                    people[client_address]=2
            else:
                data_variable = pickle.loads(data)
                global count
                global CBF_list
                count=count+1
                print("segment 10-B: number of total intersation with total CBF",CBF_list.intersection(data_variable).bitarray.count())
                if((people[client_address]==3) or (count==1) or (CBF_list.intersection(data_variable).bitarray.count()>0)):
                    if((people[client_address])!=2):
                        print("Segment 10- B: "+str(client_address)+" diagnosed positive,update data")
                        if((people[client_address])==1):client.sendall("You are diagnosed positive".encode())
                        print("Segment 10- A:receive CBF, before update",CBF_list.bitarray.count())
                        CBF_list=CBF_list.union(data_variable)
                        print("Segment 10- A:after update",CBF_list.bitarray.count())
                        people[client_address]=3
                        client.sendall("Update success".encode())
                    else:
                        print("Segment 10- B: "+str(client_address)+" diagnosed positive,reject sending")
                        client.sendall("You are diagnosed positive".encode())
                        client.sendall("You reject sending".encode())
                else:
                    print("Segment 10- B: "+str(client_address)+" are safe")
                    client.sendall("You are safe".encode())
              
        except Exception as e:
            print(e)
            remove_client(client_address)
            break
        
def remove_client(client_address):
    client = g_conn_pool[client_address]
    if None != client:
        client.close()
        g_conn_pool.pop(client_address)
        print("client offline: " + str(client_address))


if __name__ == '__main__':
    while True:
        client, client_address = g_socket_server.accept() 
        threading.Thread(target=accept_client, args=(client, client_address)).start()
