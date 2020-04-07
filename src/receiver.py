import can
import time

from cannode import Node

"""
Receiver node : Receiving, controlling the signatures and counting Rx/Tx errors
"""


class Receiver(Node):
    def __init__(self, bus_, id_, ec_, isSigned_):
        self.idnode = id_
        self.printReceiverInfo()
        self.bus = bus_
        self.ec = ec_
        self.isSigned = isSigned_

    def printReceiverInfo(self):
        """
        Print logger for debug purposes
        """
        print("-----------------")
        print("CAN NODE RECEIVER")
        print("NODE ID:"+str(self.idnode))
        print("ERROR COUNTER:"+str(0))
        print("-----------------")

    def errorTx(self, msg):
        if(not msg.is_error_frame):
            # Receive the message just transmitted to check for errors
            if(self.ec.tx_err < 256):
                self.ec.tx_err = self.ec.tx_err + 8
                self.ec.lastTx = time.time()
                self.ec.totTxErr = self.ec.totTxErr + 1

            (_, dataMsg) = self.sign(msg, self.computeData(), 0x00000000)
            # print("ERROR MSG:"+hex(encId)+" "+self.ByteToHex(dataMsg))

            # If transmission error, send error message
            errorMsg = can.Message(timestamp=msg.timestamp,
                                   arbitration_id=0x00000000,
                                   extended_id=True,
                                   is_error_frame=True,
                                   data=dataMsg)

            self.bus.send(errorMsg)

            if(self.bus.msgOnBus != []):
                self.bus.msgOnBus.pop()

    def receive(self, msg):
        """
        Receive and analyze the pakets
        """
        self.ec.totRxBus = self.ec.totRxBus + 1
        # recvID = int(self.idnode)

        # tstmp = msg.timestamp
        # print(str(self.idnode)+":"+"Rx:\t" + str(msg)
        #       + "\tRx_ERR:"+str(self.ec.rx_err))

        # print(str(self.bus.msgOnBus))
        # If received message has just been transmitted by node
        if(msg.is_error_frame):
            if(self.getIdFromSign(msg) != self.idnode):
                self.ec.rx_err = self.ec.rx_err + 1
                self.ec.lastRx = time.time()
                self.ec.totRxErr = self.ec.totRxErr + 1

        # Determine if the node should process the message
        elif(self.filterMessage(msg)):
            # If message is destined to current node, we increase the
            # number of receptions and update the last reception time
            self.ec.lastRc = time.time()
            self.ec.msgrec = self.ec.msgrec + 1

            # Determine if the message is correctly signed
            if(self.checkSign(msg)):
                self.ec.msgrecsig = self.ec.msgrecsig + 1
                # decodedId = self.getIdFromSign(msg)
                # print("SIGNED"+hex(decodedId))
                # Erroneous transmission
                # In case of a false message
                # We identify the false messages with their specified data
                if(hex(int(self.ByteToHex(msg.data[0:7]), 16))
                   == hex((int(0x123456789ABCDE)))):
                    self.errorTx(msg)

            elif(self.ec.tx_err < 256 and self.ec.tx_err > 0):
                self.ec.tx_err = self.ec.tx_err - 1
                if(self.ec.rx_err > 0):
                    self.ec.rx_err = self.ec.rx_err - 1

        elif(self.ec.rx_err > 0):
            self.ec.rx_err = self.ec.rx_err - 1

    def filterMessage(self, msg):
        """
        Determines if a given received message is destined to the node
        (Replacement of can mask)
        """
        decodedId = self.getIdFromSign(msg)

        # Get group Id
        grpId = self.getGroupFromMsgId(decodedId)

        return self.kMgr.isNodeMemberOfGroup(self.idnode, grpId)
