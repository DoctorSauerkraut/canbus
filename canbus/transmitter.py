import can
import time
import sys
import hashlib
import random
import hmac
import base64

from cannode import *
from errorcounter import *

class Transmitter(Node):
    def __init__(self,bus_,idnode_, networkNodes_, ec_, isSigned_):
        self.bus = bus_
        self.idnode = idnode_
        self.networkNodes = networkNodes_
        self.ec = ec_
        self.isSigned = isSigned_
        
    def transmit(self):
        # build a message
        tstmp  =time.time()
        sendOk = True
            
        while(sendOk==True and self.ec.tx_err < 256):            
            dest = random.randint(0,len(self.networkNodes)-1)
            
            #waitTime = random.uniform(1,10)
            waitTime = 10
            dataNotEncoded = self.computeData()
            msgId = self.computeMsgId()

            messageNotEncoded = can.Message(timestamp=tstmp,
                            arbitration_id= msgId, 
                            extended_id=True,is_error_frame=False,
                            data=dataNotEncoded)
            
            dts = str(self.ByteToHex(messageNotEncoded.data))      
            if (dts not in self.counters) :
                self.counters[dts] = 0x01
                
            (encId, dataMsg) = self.sign(messageNotEncoded, dataNotEncoded)
                  
            message = can.Message(timestamp=tstmp,
                            arbitration_id= encId, 
                            extended_id=True,
                            is_error_frame=False,
                            data=dataMsg)
            
            #Display unsigned message
            #print("--" + str(self.idnode)+":"+"Tx:\t"+str(messageNotEncoded)) 
            #Display final signed message
            #print(str(self.idnode)+":"+"Tx:\t"+str(message)+"\tTx_ERR:"+str(self.ec.tx_err))   
            self.bus.send(message)  
            self.ec.msgtra = self.ec.msgtra + 1
            self.ec.lastTr = time.time()
            #self.ec.totTxErr = self.ec.totTxErr + 1
            
            #self.bus.msgOnBus.append(message)
            time.sleep(waitTime/10)   
            
        if(self.ec.tx_err >= 256):
            print("ERROR COUNT REACHED. TRANSMISSION STOPPED.")
            return 0