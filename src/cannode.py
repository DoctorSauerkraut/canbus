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
    thread = None
    isReceiver = False

    def setThread(self, thread):
        self.thread = thread

    def ByteToHex(self, byteStr):
        return ''.join('{:02x}'.format(x) for x in byteStr)

    # Verify data signature
    def checkSign(self, msg):
        if(self.isSigned):
            dts = self.ByteToHex(msg.data[0:7])

            # Computing Message id
            idMsg = self.getIdFromSign(msg)

            # Checking if this id has already been received (replay attacks)
            toCheck = hex(int(dts, 16))

            if (idMsg in self.counters):
                try:
                    toCheck = hex(int(dts, 16) + self.counters[idMsg])[2:]
                except KeyError:
                    if(self.isReceiver):
                        self.thread.stop()
                    else:
                        self.thread.terminate()

            # Padding
            if(len(toCheck) < 14):
                toCheck = "0"+toCheck
            # print("IDMSG:"+str(idMsg)+" "+str(self.counters[idMsg]))
            
            # Computing signature
            signData = self.computeHMAC(toCheck, idMsg)

            signMsg = []
            signMsg.append(msg.data[7])
            signMsg.append(msg.arbitration_id & 0x000000FF)
            signMsg.append(msg.arbitration_id >> 8 & 0x000000FF)

            # print("IDMSG:"+str(idMsg)+" TOCHECK:"+str(toCheck)+" Sign:"+
            # self.ByteToHex(signData)
            #       +" Rec:"+self.ByteToHex(signMsg)) 

            # If computed and received signature are identical
            if(signMsg == signData):
                # Counter against replay attack increasing
                # self.counters[idMsg] = self.counters[idMsg] + 0x01
                return True
            else:
                self.ec.onebyteErr = self.ec.onebyteErr + 1
                # print("ERROR MSG:"+str(idMsg)+" TOCHECK:"+str(toCheck)+" 
                # Sign:"+self.ByteToHex(signData)) 
                # self.ec.mapErrors()
                return False
        else:
            return True

    def sign(self, msg, data, msgId):
        """
        Sign message arbitration id and last byte of data
        """
        if(self.isSigned):
            dataConverted = self.ByteToHex(msg.data)
            dts = str(dataConverted)
            # We keep in history the number of times this id has been used to
            # prevent replay attacks
            if (msgId in self.counters):
                self.counters[msgId] = self.counters[msgId] + 0x01
                toCheck = hex(int(dts, 16) + self.counters[msgId])[2:]
            else:
                toCheck = dts
                self.counters[msgId] = 0x00

            # print(type(toCheck))
            # print("SEND MSGID:"+str(msgId) + " Count:" 
            #      + str(self.counters[msgId])
            #      + " " + str(dts) + " " + str(toCheck))
 
            rst = self.computeHMAC(toCheck, msgId)

            # Encoded ID computation
            encId = (((msg.arbitration_id << 8) + rst[2]) << 8) + rst[1]

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
            binKey = self.kMgr.loadKey(self.idnode, grpId)

            # Transform the key into binary array
            # binKey = bytearray()
            # binKey.extend(map(ord, strKey))
        except UnauthorizedAccessToKey:
            print("Node "+self.idnode+" tried to access to key " + grpId)
            return

        # Specify the CAN key
        hmacComp = hmac.new(binKey, data.encode("utf-8"), hashlib.sha256)
        digest = hmacComp.digest()
        rst = (list(bytearray(digest)))
        # print("ID:"+str(msgId)+" Data:"+str(data)+" Sign"+self.ByteToHex(rst[29:32]))
        return rst[29:32]

    def computeData(self):
        data = []

        for _ in range(0, 8-SIGNLENTH):
            data.append(int(random.uniform(0, 256)))

        return data[0:8-SIGNLENTH]
