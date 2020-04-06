import can
import time
import random

from cannode import Node


class Transmitter(Node):
    def __init__(self, bus_, idnode_, networkNodes_,
                 ec_, isSigned_, totalNodes_, totalGroups_):
        self.bus = bus_
        self.idnode = idnode_
        self.networkNodes = networkNodes_
        self.ec = ec_
        self.isSigned = isSigned_
        self.totalNodes = totalNodes_
        self.totalGroups = totalGroups_

    def transmit(self):
        # build a message
        tstmp = time.time()
        sendOk = True

        while(sendOk and self.ec.tx_err < 256):
            # dest = random.randint(0, len(self.networkNodes)-1)

            # waitTime = random.uniform(1,10)
            waitTime = 10
            dataNotEncoded = self.computeData()
            msgId = self.computeMsgId()

            messageNotEncoded = can.Message(timestamp=tstmp,
                                            arbitration_id=msgId,
                                            extended_id=True,
                                            is_error_frame=False,
                                            data=dataNotEncoded)

            dts = str(self.ByteToHex(messageNotEncoded.data))
            if (dts not in self.counters):
                self.counters[dts] = 0x01

            (encId, dataMsg) = self.sign(messageNotEncoded,
                                         dataNotEncoded,
                                         msgId)

            message = can.Message(timestamp=tstmp,
                                  arbitration_id=encId,
                                  extended_id=True,
                                  is_error_frame=False,
                                  data=dataMsg)

            # Display unsigned message
            # print("--" + str(self.idnode)+":"+"Tx:\t"+str(messageNotEncoded))

            # Display final signed message
            print(str(self.idnode)+":"+"Tx:\t"
                  + str(message)+"\tTx_ERR:"+str(self.ec.tx_err))

            self.bus.send(message)
            self.ec.msgtra = self.ec.msgtra + 1
            self.ec.lastTr = time.time()
            # self.ec.totTxErr = self.ec.totTxErr + 1

            # self.bus.msgOnBus.append(message)
            time.sleep(waitTime/10)

        if(self.ec.tx_err >= 256):
            print("ERROR COUNT REACHED. TRANSMISSION STOPPED.")
            return 0

    def computeMsgId(self):
        """
        Computes the message id destination for a message
        """
        return random.randint(1, self.totalNodes)
