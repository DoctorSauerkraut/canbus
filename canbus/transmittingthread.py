import threading
import time
from transmitter import Transmitter

class TransmittingThread(threading.Thread):
    bus = None
    idnode = 0
    networkNodes = []
    isSigned = False
    totalNodes = 0

    def __init__(self,bus_,idnode_, networkNodes_, ec_, isSigned_, totalNodes_):
        threading.Thread.__init__(self)
        self.bus = bus_
        self.idnode = idnode_
        self.networkNodes = networkNodes_
        self.ec = ec_
        self.isSigned = isSigned_
        self.totalNodes = totalNodes_
        
    def run(self):        
        trans = Transmitter(self.bus, self.idnode, self.networkNodes, self.ec, self.isSigned, self.totalNodes)
        trans.transmit()
