import random

from netjob.broadcast import BroadcastReceiver
from netjob.client import Client
import multiprocessing

import imagemanip

clients = []
maxCliPerSv = multiprocessing.cpu_count()

#Random ID for this Process
myProcID = random.getrandbits(128)

if __name__ == "__main__":
    broadcastGroup = "239.192.1.100"
    broadcastPort = 50000
    
    receiver = BroadcastReceiver(broadcastGroup, broadcastPort)
    
    print("ID:", myProcID)
    print("Receiver created! Waiting for broadcast messages...")

    while True:
        svIP, svPort = receiver.pollRequest(0.05)

        for cliID in range(maxCliPerSv):
            if svIP and svPort and (svIP, svPort, myProcID+cliID) not in clients:
                try:
                    client = Client(svIP, svPort, myProcID+cliID, lambda x: clients.remove((x.ipPortPair()[0], x.ipPortPair()[1], x.getProcID())))
                except ConnectionRefusedError:
                    print("Failed: Server not running or not reachable!")
                except TimeoutError:
                    print("Failed: Connection timeout!")
                else:
                    print(svIP, ":", svPort, "Connected")
                    clients.append((svIP, svPort, myProcID+cliID))
