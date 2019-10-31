import threading
import time
from transmitter import *

class TransmittingThread(threading.Thread):
    bus = None
    idnode = 0
    networkNodes = []
    isSigned = False
    
    def __init__(self,bus_,idnode_, networkNodes_, ec_, isSigned_):
        threading.Thread.__init__(self)
        self.bus = bus_
        self.idnode = idnode_
        self.networkNodes = networkNodes_
        self.ec = ec_
        self.isSigned = isSigned_
        
    def run(self):
        loop = 0
        
        trans = Transmitter(self.bus, self.idnode, self.networkNodes, self.ec, self.isSigned)
        trans.transmit()
