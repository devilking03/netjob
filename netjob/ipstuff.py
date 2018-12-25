import socket
import struct

BUFF_SIZE = 4096

#https://stackoverflow.com/a/1267524
def getLocalIP():
    return ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

def udpSock():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

def tcpSock():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sendLength(s, buffer):
    lengthPack = struct.pack('>Q', len(buffer))
    s.sendall(lengthPack)
    s.sendall(buffer)

def recvLength(s):
    resLen = s.recv(8)
    (dlength,) = struct.unpack('>Q', resLen)
    buffer = b''

    while len(buffer) < dlength:
        toRead = dlength - len(buffer)
        buffer += s.recv(BUFF_SIZE if toRead > BUFF_SIZE else toRead)
    
    return buffer


def recvTillEnd(s):
    message = b''
    recvData = bytearray(BUFF_SIZE)
    while True:
        recvlen = s.recv_into(recvData, BUFF_SIZE)
        message += recvData[:recvlen]
        if recvlen < BUFF_SIZE:
            break
    return message
