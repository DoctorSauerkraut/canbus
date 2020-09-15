import threading
from receiver import Receiver
from can import Notifier
from msglistener import MsgListener


class ReceivingThread(threading.Thread):
    bus = None
    idnode = 0
    isSigned = True
    notifier = None

    def __init__(self, bus_, idnode_, ec_, isSigned_):
        threading.Thread.__init__(self)
        self.bus = bus_
        self.idnode = idnode_
        self.ec = ec_
        self.isSigned = isSigned_

    def getNotifier(self):
        return self.notifier

    def run(self):
        # Initiate receiver
        rec = Receiver(self.bus, self.idnode, self.ec, self.isSigned)

        self.notifier = Notifier(self.bus, [MsgListener(rec)])
        rec.setThread(self.notifier)
