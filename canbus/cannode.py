import can
import sys
import time
import hashlib
import random
import hmac
import base64

SIGNLENTH = 1

class Node:
    isSigned = False
    bus = None
    idnode = 0
    counters = {}
    
    ec = None # Error counter
    #Currently transmitting message
    networkNodes = []
    
    def ByteToHex(self, byteStr ):
        return ''.join('{:02x}'.format(x) for x in byteStr)
    
    # Verify data signature    
    def checkSign(self, msg):
        if(self.isSigned == True):
            dts = str(self.ByteToHex(msg.data[0:7]))
            if (dts in self.counters ):
                toCheck = dts + str(self.counters[dts])
            else:
                toCheck = dts
            #print("ID:"+str(self.idnode)+" COUNTER:"+str(self.counters[dts]))
            signData = self.computeHMAC(toCheck)
            
            signMsg= []
            signMsg.append(msg.data[7])
            signMsg.append(msg.arbitration_id&0x000000FF)
            signMsg.append(msg.arbitration_id>>8&0x000000FF)
             
            # arb_id = msg.arbitration_id >> 16      
            
            # print("DATA:"+dts+" SIGN:"+self.ByteToHex(signData))
            
            if(signMsg == signData)   :
                self.counters[dts] = self.counters[dts] + 0x01
                #print("ID:"+str(self.idnode)+" SIGN OK")
                #Counter against replay attack increasing
                dts = str(self.ByteToHex(msg.data))      
                if(dts in self.counters):
                    self.counters[dts] =  self.counters[dts] + 0x01
                return True
            elif(signMsg[0] == signData[0]):
                self.ec.onebyteErr = self.ec.onebyteErr + 1
                self.ec.mapErrors()
                #print("1 B Error at time:"+hex(signMsg[0])+" "+hex(signData[0])+ " "+str(msg))
            return False
        else :
            return True
    
    #Sign message arbitration id and last byte of data
    def sign(self,msg, data):
        if(self.isSigned == True):
            dataConverted = self.ByteToHex(msg.data)
            
            dts = str(dataConverted + str(self.counters[str(dataConverted)]))
            #print("INIT DATA:"+str(dataConverted))
            #print("DATA TO SIGN:"+str(dts))
            #print("COUNTER:"+str(self.counters[str(dataConverted)]))
            rst = self.computeHMAC(dts)
               
            #print("SIGNATURE:"+ " "+hex(rst[2])+" "+hex(rst[1])+" "+hex(rst[0]))
            encId = (((msg.arbitration_id << 8)+ rst[2])<< 8) + rst[1]
            
            #print("ARB ID:"+hex(msg.arbitration_id)+" ENC ID:"+hex(encId))
            return (encId, data+[rst[0]])
        else:
            return(msg.arbitration_id, data)
        
    #Compare transmitted with received message when same id
    def checkTransmission(self, mTrans):
        for j in range(len(self.bus.msgOnBus)) :
            if(self.bus.msgOnBus != []):
               #print(str(self.bus.msgOnBus[j].data))
                if(self.bus.msgOnBus[j].data == mTrans.data):
                    self.bus.msgOnBus.remove(self.bus.msgOnBus[j])
                    return True
        return False
    
    def getIdFromSign(self, msg):
        if(self.isSigned==True):
            self.computeHMAC(str(self.ByteToHex(msg.data)))
            arb_id = (msg.arbitration_id)>>16
            return (arb_id<<16)
        else:
            return msg.arbitration_id
        
    #Compute HMAC from 7 bytes of data and keep the last byte of digest   
    def computeHMAC(self, data):
        rst = []
        #print("DATA HMAC:"+str(data))
        
        #Specify the CAN key
        digest = hmac.new(b'0123456789', data.encode("utf-8"), hashlib.sha256).digest()
        rst = (list(bytearray(digest)))
        #print(self.ByteToHex(rst))
        return rst[29:32]
        
    def computeData(self):
        data=[]

        for _ in range(0,8-SIGNLENTH):
            data.append(int(random.uniform(0,256)))
            #data.append(i)
            
        data = [0x02, 0xdd, 0xe2, 0x52, 0xb0, 0x8d, 0xc6]
        return data[0:8-SIGNLENTH]
    
    def computeMsgId(self):
        r = int(random.uniform(0,len(self.networkNodes)+1))
        return 0x1230 + r
    