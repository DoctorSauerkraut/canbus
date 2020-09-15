import time
import math


class ErrorCounter:
    tx_err = 0
    rx_err = 0
    lastTr = 0
    lastRc = 0
    lastTx = time.time()
    lastRx = time.time()
    lastOb = time.time()
    
    msgtra = 0
    totTxErr = 0
    totRxErr = 0
    onebyteErr = 0
    # Received messages on the bus
    totRxBus = 0
    # Received messages destined to the node
    msgrec = 0
    # Received messages correctly signed
    msgrecsig = 0
    errorsDelay = {}

    """
    def mapErrors(self):
        t = time.time()
        diff = t - self.lastOb
        self.lastOb = t
        diff = math.floor(diff*1000)
        if (str(diff) in self.errorsDelay):
            self.errorsDelay[str(diff)] = self.errorsDelay[str(diff)] + 1
        else:
            self.errorsDelay[str(diff)] = 1
        # print(self.errorsDelay)
        file=open("log.txt","w")
        for i in self.errorsDelay:    
            file.write(str(i)+"\t"+str(self.errorsDelay[str(i)])+"\n")
        file.close()
    """