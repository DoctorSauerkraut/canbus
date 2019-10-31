import can
import sys
import hashlib
import random
import hmac
import base64
import time

from cannode import *
from msglistener import *

"""Receiver node : Receiving, controlling the signatures and counting Rx/Tx errors"""
class Receiver(Node):
    def __init__(self, bus_, id_, ec_, isSigned_):
        self.idnode = id_
        self.printReceiverInfo()
        self.bus = bus_
        self.ec = ec_
        self.isSigned = isSigned_
        
    def printReceiverInfo(self):
        print("-----------------")
        print("CAN NODE RECEIVER")
        print("NODE ID:"+str(self.idnode))
        print("ERROR COUNTER:"+str(0))
        print("-----------------")
     
    def errorTx(self, msg):  
        if(msg.is_error_frame == False):
            #Receive the message just transmitted to check for errors
            if(self.ec.tx_err < 256):
                self.ec.tx_err = self.ec.tx_err + 8
                self.ec.lastTx = time.time()
                self.ec.totTxErr = self.ec.totTxErr + 1

            (encId, dataMsg) = self.sign(msg, self.computeData())
            #print("ERROR MSG:"+hex(encId)+" "+self.ByteToHex(dataMsg))
            
            #If transmission error, send error message
            errorMsg = can.Message(timestamp=msg.timestamp,
                                arbitration_id=0x00000000, 
                                extended_id=True,
                                is_error_frame=True,
                                data=dataMsg)
            
            self.bus.send(errorMsg)
            
            if(self.bus.msgOnBus != []):
                self.bus.msgOnBus.pop()   
        
    """Receive and analyze the pakets"""
    def receive(self, msg):
        bufferMsg = []
        self.ec.lastRc = time.time()
        self.ec.msgrec = self.ec.msgrec + 1
        recvID = int(self.idnode)
  
        tstmp = msg.timestamp
                
        #print(str(self.idnode)+":"+"Rx:\t"+str(msg)+"\tRx_ERR:"+str(self.ec.rx_err))
        #print(str(self.bus.msgOnBus))
        # If received message has just been transmitted by node
        if(msg.is_error_frame):
            if(self.getIdFromSign(msg) != self.idnode):
                self.ec.rx_err = self.ec.rx_err +1
                self.ec.lastRx = time.time()
                self.ec.totRxErr = self.ec.totRxErr + 1
            
        elif(self.checkSign(msg)):
            decodedId = self.getIdFromSign(msg)
            #print(str(self.idnode)+"DECODED:"+hex(decodedId)+"/"+hex(self.bus.filters[0]["can_id"]))
            if((decodedId == self.bus.filters[0]["can_id"])):    
             #   print("SIGNED"+hex(decodedId))
                #Erroneous transmission
                #In case of a false message
                #We identify the false messages with their specified data
                if(hex(int(self.ByteToHex(msg.data[0:7]), 16)) == hex((int(0x123456789ABCDE)))):
                    self.errorTx(msg)

            elif(self.ec.tx_err < 256 and self.ec.tx_err > 0):
                self.ec.tx_err = self.ec.tx_err - 1             
                if(self.ec.rx_err > 0):
                    self.ec.rx_err = self.ec.rx_err - 1

        elif(self.ec.rx_err > 0):
            self.ec.rx_err = self.ec.rx_err - 1
        
      
        