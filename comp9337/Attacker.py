import socket
from threading import Thread


udpserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
# Enable broadcasting mode
udpserver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udpserver.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)

udpserver.bind(('', 80))
def sendFlood():
    while True:
        data = udpserver.recv(1024)
        udpserver.sendto(data, ('<broadcast>', 80))


if __name__ == '__main__':
    thread = Thread(target=sendFlood)
    thread.setDaemon(True)
    thread.start()
    while True:
        pass
