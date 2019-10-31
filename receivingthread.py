import threading
import time
from receiver import *

class ReceivingThread(threading.Thread):
    bus = None
    idnode = 0
    isSigned = True
    
    def __init__(self,bus_,idnode_, ec_, isSigned_):
        threading.Thread.__init__(self)
        self.bus = bus_
        self.idnode = idnode_
        self.ec = ec_
        self.isSigned = isSigned_
        
    def run(self):
        # Initiate receiver
        rec = Receiver(self.bus, self.idnode, self.ec, self.isSigned)
        notifier = can.Notifier(self.bus, [MsgListener(rec)])