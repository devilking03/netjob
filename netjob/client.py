import threading
from netjob import ipstuff
from netjob import buffer
from netjob import job


class Client(threading.Thread):
    __destIP = ""
    __destPort = 0
    __running = False

    def __init__(self, ipadd, port, procID = None, onDone = None):
        super(Client, self).__init__()
        
        self.__destIP = ipadd
        self.__destPort = port
        self.__procID = procID
        self.__doneCallback = onDone
        
        self.__sock = ipstuff.tcpSock()
        self.__sock.connect(self.ipPortPair())

        self.__running = True
        self.daemon = True
        self.start()

    def ipPortPair(self):
        return (self.__destIP, self.__destPort)

    def getProcID(self):
        return self.__procID

    def run(self):
        while self.__running:
            try:
                responseData = []

                '''jobBinary = b''
                while True:
                    #print("Reading")
                    jobBinary += ipstuff.recvTillEnd(self.__sock)

                    if len(jobBinary) == 0:
                        self.__running = False
                        break
                
                    header = jobBinary[:job.HEADER_ALIGN].decode()
                    dataLen = 0

                    if "JOB" in header:
                        lines = header.splitlines()
                        dataLen = int([s.split(':')[-1] for s in lines if "length" in s.lower()][-1].strip())
                        if len(jobBinary[job.HEADER_ALIGN:]) < dataLen:
                            print("Incomplete")
                        else:
                            pickleData = jobBinary[job.HEADER_ALIGN:(job.HEADER_ALIGN+dataLen)]
                            if len(pickleData) == dataLen and not dataLen == 0 and jobBinary[(job.HEADER_ALIGN+dataLen):(job.HEADER_ALIGN+dataLen+3)] == b'END':
                                break

                        #raise RuntimeError("Incomplete or Malformed data received")
                    #else:
                        #raise RuntimeError("Header and Footer doesn't seem right, got\n{}\n----AND----\n{}".format(header, jobBinary[-3:]))
                '''
                pickleData = ipstuff.recvLength(self.__sock)

                #print("Reading again")
                jobObj = buffer.deserializeObject(pickleData)

                if jobObj.SIGNATURE == job.SerializableJob.SIGNATURE:
                    responseData = jobObj.doAction()
                else:
                    raise RuntimeError("Signature Mismatch")

                if responseData is None:
                    responseData = []

                SData = buffer.serializeObject(responseData)
                ipstuff.sendLength(self.__sock, SData)
                
            except ConnectionResetError:
                print("Connection dropped")
                break
            except (RuntimeError, EOFError) as ex:
                #TODO: Ask to resend instead of dropping
                print(jobObj.getFn())
                print("Packet Loss or Malformed Job received:", ex)
                break
            #except:
            #    print("IDK some error occured")
            #    break
            
        self.__sock.close()
        if self.__doneCallback:
            self.__doneCallback(self)
