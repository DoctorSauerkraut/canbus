import hashlib
import random
import hmac

from keymanager import KeyManager
from exceptions import UnauthorizedAccessToKey

SIGNLENTH = 1


class Node:
    isSigned = False
    bus = None
    idnode = 0
    counters = {}
    totalNodes = 0
    kMgr = KeyManager()
    totalGroups = 0
    ec = None  # Error counter
    # Currently transmitting message
    networkNodes = []

    def ByteToHex(self, byteStr):
        return ''.join('{:02x}'.format(x) for x in byteStr)

    # Verify data signature
    def checkSign(self, msg):
        if(self.isSigned):
            dts = str(self.ByteToHex(msg.data[0:7]))
            if (dts in self.counters):
                toCheck = dts + str(self.counters[dts])
            else:
                toCheck = dts

            # print("ID:"+str(self.idnode)+" COUNTER:"+str(self.counters[dts]))
            # print("ARB ID:"+hex(msg.arbitration_id))
            idMsg = self.getIdFromSign(msg)
            # print("ID:"+str(idMsg))
            signData = self.computeHMAC(toCheck, idMsg)

            signMsg = []
            signMsg.append(msg.data[7])
            signMsg.append(msg.arbitration_id & 0x000000FF)
            signMsg.append(msg.arbitration_id >> 8 & 0x000000FF)

            # arb_id = msg.arbitration_id >> 16
            # print("DATA:"+dts+" SIGN:"+self.ByteToHex(signData))

            if(signMsg == signData):
                self.counters[dts] = self.counters[dts] + 0x01
                # print("ID:"+str(self.idnode)+" SIGN OK")
                # Counter against replay attack increasing
                dts = str(self.ByteToHex(msg.data))
                if(dts in self.counters):
                    self.counters[dts] = self.counters[dts] + 0x01
                return True
            elif(signMsg[0] == signData[0]):
                self.ec.onebyteErr = self.ec.onebyteErr + 1
                self.ec.mapErrors()
                # print("1 B Error at time:"+hex(signMsg[0])+" "
                # +hex(signData[0])+ " "+str(msg))
            return False
        else:
            return True

    def sign(self, msg, data, msgId):
        """
        Sign message arbitration id and last byte of data
        """
        if(self.isSigned):
            dataConverted = self.ByteToHex(msg.data)
            dts = str(dataConverted + str(self.counters[str(dataConverted)]))
            rst = self.computeHMAC(dts, msgId)

            # Encoded ID computation
            encId = (((msg.arbitration_id << 8) + rst[2]) << 8) + rst[1]

            # Sent message logging
            # print("INIT DATA:" + str(dataConverted))
            # print("DATA TO SIGN:" + str(dts))
            # print("COUNTER:" + str(self.counters[str(dataConverted)]))
            # print("MSG ID:" + str(msgId))
            # print("NODE:" + str(self.idnode))
            # print("SIGNATURE:" + " " + hex(rst[2]) + " "
            #       + hex(rst[1]) + " " + hex(rst[0]))
            # print("ARB ID:"+hex(msg.arbitration_id)+" ENC ID:"+hex(encId))
            return (encId, data+[rst[0]])
        else:
            return (msg.arbitration_id, data)

    def checkTransmission(self, mTrans):
        """
        Compare transmitted with received message when same id
        """
        for j in range(len(self.bus.msgOnBus)):
            if(self.bus.msgOnBus != []):
                # print(str(self.bus.msgOnBus[j].data))
                if(self.bus.msgOnBus[j].data == mTrans.data):
                    self.bus.msgOnBus.remove(self.bus.msgOnBus[j])
                    return True
        return False

    def getIdFromSign(self, msg):
        if(self.isSigned):
            arb_id = (msg.arbitration_id) >> 16
            return (arb_id)
        else:
            return msg.arbitration_id

    def getGroupFromMsgId(self, msgId):
        """
        Get group id from msg id
        Interface between transmitter/receiver and key manager
        """
        return self.kMgr.getGrpIdFromMsgId(msgId)

    def computeHMAC(self, data, msgId):
        """
        Computes HMAC from 7 bytes of data and keep the last byte of digest
        """
        rst = []
        # Get the group ID
        grpId = self.getGroupFromMsgId(msgId)

        try:
            # Load the key
            strKey = self.kMgr.loadKey(self.idnode, grpId)

            # Transform the key into binary array
            binKey = bytearray()
            binKey.extend(map(ord, strKey))
        except UnauthorizedAccessToKey:
            print("Node "+self.idnode+" tried to access to key "+str(strKey))
            return

        # Specify the CAN key
        hmacComp = hmac.new(binKey, data.encode("utf-8"), hashlib.sha256)
        digest = hmacComp.digest()
        rst = (list(bytearray(digest)))

        # print(self.ByteToHex(rst))
        return rst[29:32]

    def computeData(self):
        data = []

        for _ in range(0, 8-SIGNLENTH):
            data.append(int(random.uniform(0, 256)))

        return data[0:8-SIGNLENTH]
