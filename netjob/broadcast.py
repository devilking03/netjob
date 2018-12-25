import socket
from time import sleep
import threading
from netjob import ipstuff
import struct
import queue

class Broadcaster(threading.Thread):
    __running = False
    __ended = False
    __bGrpAddr = ("", 0)
    __bRate = 10
    __redirectAddr = ("", 0)
    
    def __init__(self, broadcastGroup, broadcastPort, redirectTo, broadcastRate=10):
        super(Broadcaster, self).__init__()

        self.__bGrpAddr = (broadcastGroup, broadcastPort)
        self.__bRate = broadcastRate
        self.__redirectAddr = redirectTo
        
        self.__sock = ipstuff.udpSock()
        self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
        self.__running = True
        self.daemon = True

        self.start()

    def getHeader(self):
        return '''HAI
I HAS IP ''' + self.__redirectAddr[0] + '''
AND HAS PORT ''' + str(self.__redirectAddr[1]) + '''
K? AWSUM THX
KTHXBYE'''

    def run(self):
        while self.__running:
            try:
                self.__sock.sendto(self.getHeader().encode(), self.__bGrpAddr)
            except:
                print("Error :(")
                self.__running = False
                break
            sleep(1/self.__bRate)

        self.__sock.close()
        self.__ended = True

    def stop(self):
        self.__running = False
        while not self.__ended:
            pass

class BroadcastReceiver(threading.Thread):
    __ended = False
    __running = False
    __callbackFn = None
    __clientQueue = queue.Queue()
    
    def __init__(self, broadcastGroup, broadcastPort, clientCallback = None):
        super(BroadcastReceiver, self).__init__()
        
        self.__sock = ipstuff.udpSock()
        self.__bGrpAddr = (broadcastGroup, broadcastPort)
        self.__callbackFn = clientCallback

        try:
            self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass

        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        self.__sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        self.__sock.bind(('', broadcastPort))

        #Join Multicast Group
        group = socket.inet_aton(broadcastGroup)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        self.__running = True
        self.daemon = True

        self.start()

    def pollRequest(self, timeout=None):
        try:
            clientReq = self.__clientQueue.get(timeout=timeout)
        except queue.Empty:
            return (None, None)
        else:
            self.__clientQueue.task_done()
            return clientReq

    def stop(self):
        self.__running = False
        while not self.__ended:
            pass
        
    def run(self):
        while self.__running:
            data = ipstuff.recvTillEnd(self.__sock)
            message = data.decode()

            if "HAI" in message:
                lines = message.splitlines()
                listenIP = str([s.split(' ')[-1] for s in lines if "ip" in s.lower()][-1])
                listenPort = int([s.split(' ')[-1] for s in lines if "port" in s.lower()][-1])
                self.__clientQueue.put((listenIP, listenPort))

                #if self.__callbackFn:
                #    self.__callbackFn(listenIP, listenPort)

        self.__ended = True
        self.__sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.__bGrpAddr[0]) + socket.inet_aton("0.0.0.0"))
        self.__sock.close()
