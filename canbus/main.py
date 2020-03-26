from receivingthread import *
from transmittingthread import *
import can
import sys
import os
from os import system, name 
import json

from canbus import *

"""
@author Olivier Cros
CAN BUS Simulation Main file
Launching simulation and logging machine
"""

def launchNode(nodeId, canFilter, networkNodes, isSigned, params):
    """
    Initializing the bus interface
    and preparing the reception and transmission threads
    """
    bus = CanBUS(interface='socketcan',
                  channel=params["channel"],
                  can_filters=canFilter,
                  receive_own_messages=True) 
    
    bus.set_filters(canFilter)
    ec = ErrorCounter()

    recThread = ReceivingThread(bus, nodeId, ec, isSigned)
    transThread = TransmittingThread(bus, nodeId, networkNodes, ec, isSigned)
    
    # Starting reception thread
    if(params["reception"] == True):
        print("Starting the receiver")
        recThread.start()
    
    # Starting transmission thread
    if(params["transmission"] == True):
        print("Starting the transmitter")
        transThread.start()
    
    return (recThread,transThread)
 
    
def prepareSim(params):
    """
    Setting up the network nodes and the filters applied to it
    """
    networkNodes = []
    for i in range(0, params["nbNodes"]):
        networkNodes.append((params["id"]+i, params["sign"]))
        
    #Receiver mask
    if(params["sign"]==True):
        canFilter=  [{"can_id": 0x12300000, "can_mask": 0x1FFF0000}]
    else:
        canFilter=  [{"can_id": 0x00001230, "can_mask": 0x00001FFF}]
    #initialize thread list
    threads=[]
    
    filters = []
    # create a bus instance
    for k in range(len(networkNodes)):        
        if(params["sign"]==True):
            canFilter[0]["can_id"] = canFilter[0]["can_id"]+0x00010000
            newfilt = [{"can_id": canFilter[0]["can_id"] , "can_mask": 0x1FFF0000}] 
        else:
            newfilt = [{"can_id": canFilter[0]["can_id"]+k , "can_mask": 0x00001FF0}] 
        
        filters.append(newfilt)
        threads.append(launchNode(networkNodes[k][0], newfilt, networkNodes, networkNodes[k][1], params))
        
    return (threads, filters, networkNodes)

def logSim(threads, filters, networkNodes, params):
    """
    Simulation logging-dedicated function
    """
    nbNodes = params["nbNodes"]
    #Display network current state
    system("clear")
    currentTime = time.time()
    d = round(currentTime-params["startTime"], 3)

    print("Node\t+Tx_err\t+Rx_err\t+Tot Tx\t+Tot Rx\t+1b err\t+Status\t+Signed\t+Tx del + Rx del + Rec \t+ Tra \t+ ID \t\t+ Mask \t\t+Tx err \t+Rx err \t+")

    #monitoring purposes
    statusCount =  {"OK":0,"PASS":0,"OFF":0}
    errorsCount = {"TXMAX":0,"RXMAX":0,"TXAVG":0, "RXAVG":0, "1B":0}
    totErrOneB = 0
    
    for i in range(len(threads)):
        errc = threads[i][0].ec
        status = "OK"

        if(errc.rx_err > 127 or errc.tx_err > 127):
            status = "PASS"

        if(errc.tx_err > 255):
            status = "OFF"      

        print(str(networkNodes[i][0])
              + "\t+" + str(errc.tx_err) 
              + "\t+" + str(errc.rx_err) 
              + "\t+" + str(errc.totTxErr) 
              + "\t+" + str(errc.totRxErr) 
              + "\t+" + str(errc.onebyteErr)
              + "\t+" + status
              + "\t+" + str(networkNodes[i][1])
              + "\t+" + (str(round(currentTime - errc.lastTr, 3)) if (params["transmission"] == True) else "-")
              + "\t+" + (str(round(currentTime - errc.lastRc, 3)) if (params["reception"] == True) else "-")
              + "\t+" + str(errc.msgrec) 
              + "\t+" + str(errc.msgtra)
              + "\t+"  + hex(filters[i][0]["can_id"])
              + "\t+"  + hex(filters[i][0]["can_mask"])
              + "\t+" + (str(round(currentTime - errc.lastTx, 3)) if (params["transmission"] == True) else "-")
              + "\t+" +  (str(round(currentTime - errc.lastRx, 3)) if (params["reception"] == True) else "-"))
        
        totErrOneB = totErrOneB + errc.onebyteErr
        
        statusCount[status] = statusCount[status] + 1
        if(errc.tx_err > errorsCount["TXMAX"]):
            errorsCount["TXMAX"] = errc.tx_err
        if(errc.rx_err > errorsCount["RXMAX"]):
            errorsCount["RXMAX"] = errc.rx_err
            
        errorsCount["TXAVG"] = errorsCount["TXAVG"] + errc.tx_err
        errorsCount["RXAVG"] = errorsCount["RXAVG"] + errc.rx_err
        errorsCount["1B"] = errorsCount["1B"] + errc.onebyteErr  
      
    print("------------------------------------------------")   
    print("Time: "+str(d)+" s")
    print("Status Nodes:"+str(nbNodes)
          + " OK:"+str(statusCount["OK"])
          + " PASS:"+str(statusCount["PASS"])
          + " OFF:"+str(statusCount["OFF"]))
    
    print("Errors Tx MAX:"+str(errorsCount["TXMAX"]) 
          + " \tAVG:"+str(errorsCount["TXAVG"]/nbNodes)
          + " \tRx MAX:"+str( errorsCount["RXMAX"])
          +  "\tAVG:"+str(errorsCount["RXAVG"]/nbNodes))

    return errorsCount

def launchSim(params):
    """ 
    Launching the simulation for a given time
    """
    #initialize thread list and prepare simulation
    threads, filters, networkNodes = prepareSim(params)

    j=0
    params["startTime"] = time.time()
    errorsCount = {}
    
    while (params["verbose"]==True and (time.time()-params["startTime"])<params["delay"]):
        currentTime = time.time()      
        errorsCount = logSim(threads, filters, networkNodes, params)
        timeVal = currentTime-params["startTime"]
        timeVal = round(timeVal*100)/100
        j = j+1
        time.sleep(0.5)   
        
    #file.close()
    return errorsCount

if __name__ == "__main__": 
    """
    Opening the JSON config file and preparing the simulation
    """
    #JSON Config loading
    with open('config.json', 'r') as f:
        params = json.load(f)
    
    startTime = time.time()  
    
    #Start the simulation
    errorsCount = launchSim(params)     