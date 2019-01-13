import socket
import threading
import queue

from netjob import ipstuff
from netjob import job
from netjob import broadcast
from netjob import buffer

class ClientHandle(threading.Thread):
    __conn = 0
    __addr = []
    clientConns = []
    quitClient = False

    def __init__(self, connection, destAddr, jobQueue, initJob):
        super(ClientHandle, self).__init__()
        ClientHandle.clientConns.append(connection)

        self.__conn = connection
        self.__addr = destAddr
        self.__jobQueue = jobQueue
        self.__initJob = initJob
        
        self.daemon = True
        self.start()

    def remove(connection):
        if connection in ClientHandle.clientConns:
            connection.close()
            ClientHandle.clientConns.remove(connection)

    def handleJob(self, job, jQueue = None):
        try:
            ipstuff.sendLength(self.__conn, job.getJobPack())
            message = ipstuff.recvLength(self.__conn)
            
            #TODO: Resend on fail
            job.fireCallback(message)
        except ConnectionResetError:
            print(self.__addr, "- Connection Lost!")
            if jQueue:
                jQueue.put(job)   #Put back job for someone else
            return 1
        except ConnectionAbortedError:
            print("Connection Terminated by worker")
            if jQueue:
                jQueue.put(job)
            return 2
        finally:
            if jQueue:
                jQueue.task_done()
        return 0

    def run(self):
        #TODO: Get ID for Profiling (jobs/second, data rate, etc)

        if self.__initJob:
            self.handleJob(self.__initJob)
        
        while True:
            try:
                job = self.__jobQueue.get(timeout=0.05)
                aaa = self.handleJob(job, self.__jobQueue)
                if not aaa == 0:
                    break
                
            except queue.Empty:
                pass
            if self.quitClient:
                break
            
        ClientHandle.remove(self.__conn)


class Server(threading.Thread):
    #TODO: Non-static
    __initJob = None
    __stopped = False
    __running = False
    
    def __init__(self, port, maxConns = 128, initJob = None, maxqueue = 100):
        super(Server, self).__init__()
        
        self.__jobsToDo = queue.Queue(maxsize=maxqueue)
        self.__initJob = initJob

        self.__serverSock = ipstuff.tcpSock()
        self.__serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__serverSock.bind(("", port))
        self.__serverSock.listen(maxConns)

        self.daemon = True
        self.__running = True
        self.start()

    def getSock(self):
        return self.__serverSock

    def getListenPort(self):
        return self.__serverSock.getsockname()[1]

    def stop(self):
        self.__running = False
        self.__serverSock.close()
        while not self.__stopped:
            pass

    def waitTillDone(self):
        self.__jobsToDo.join()

    def pushJob(self, job):
        self.__jobsToDo.put(job)

    def run(self):
        print("Listening...")
        while self.__running:
            try:
                conn, addr = self.__serverSock.accept()
                ClientHandle(conn, addr, self.__jobsToDo, self.__initJob)
                print(addr[0] + " connected")
            except OSError:
                break

        conn.close()
        self.__serverSock.close()

        for client in ClientHandle.clientConns:
            client.quitClient = True
        
        self.__stopped = True
