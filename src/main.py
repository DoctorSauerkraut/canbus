import time
import json

from canbus import CanBUS

from receivingthread import ReceivingThread
from transmittingthread import TransmittingThread
from errorcounter import ErrorCounter
import config
from logger import Logger

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
    totalNodes = params["totalNodes"]
    totalGroups = params["groups"]

    recThread = ReceivingThread(bus, nodeId, ec, isSigned)
    transThread = TransmittingThread(bus, nodeId, networkNodes,
                                     ec, isSigned, totalNodes, totalGroups)

    # Starting reception thread
    print("Launching the nodes ")
    if(params["reception"]):
        print("Starting the receiver " + str(nodeId))
        recThread.start()

    # Starting transmission thread
    if(params["transmission"]):
        print("Starting the transmitter " + str(nodeId))
        transThread.start()
        
    return (recThread, transThread)


def prepareSim(params):
    """
    Setting up the network nodes and the filters applied to it
    """
    networkNodes = []
    for i in range(0, params["nbNodes"]):
        networkNodes.append((params["id"]+i, params["sign"]))

    node_id = params["id"]

    # Receiver mask
    if(params["sign"]):
        # canFilter = [{"can_id": (node_id << 16), "can_mask": 0x000000000}]
        canFilter = [{"can_id": 0x00000000, "can_mask": 0x000000000}]
    else:
        canFilter = [{"can_id": 0x1230 + node_id, "can_mask": 0x00001FFF}]

    # Initialize thread list
    threads = []

    filters = []

    # create a bus instance
    for k in range(len(networkNodes)):
        if(params["sign"]):
            # canFilter[0]["can_id"] = canFilter[0]["can_id"]+0x00010000
            # newfilt = [{"can_id": canFilter[0]["can_id"],
            #            "can_mask": 0x000000000}]
            newfilt = [{"can_id":  0x000000000,
                        "can_mask": 0x000000000}]
        else:
            newfilt = [{"can_id": canFilter[0]["can_id"] + k,
                        "can_mask": 0x00001FF0}]

        filters.append(newfilt)
        threads.append(launchNode(networkNodes[k][0],
                                  newfilt,
                                  networkNodes,
                                  networkNodes[k][1],
                                  params))
    
    return (threads, filters, networkNodes)


def launchSim(params):
    """
    Launching the simulation for a given time
    """
    # nitialize thread list and prepare simulation
    threads, filters, networkNodes = prepareSim(params)

    j = 0
    params["startTime"] = time.time()
    errorsCount = {}

    while (params["verbose"]
           and (time.time() - params["startTime"]) < params["delay"]):
        currentTime = time.time()

        if(params["verbose"]):
            logger = Logger()
            errorsCount = logger.logSim(threads, filters, networkNodes, params)
        errorsCount = 0
        timeVal = currentTime-params["startTime"]
        timeVal = round(timeVal*100)/100
        j = j+1
        time.sleep(0.5)

    # file.close()
    return errorsCount


if __name__ == "__main__":
    """
    Opening the JSON config file and preparing the simulation
    """
    # JSON Config loading
    with open(config.CONFIGPATH + 'config.json', 'r') as f:
        params = json.load(f)

    startTime = time.time()

    # Start the simulation
    errorsCount = launchSim(params)
