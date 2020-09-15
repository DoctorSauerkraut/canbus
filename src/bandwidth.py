# Bandwidth monitor
import time

delta = 0
ts = []

# CAN packet size in bytes
psize = 16

# Nb of packets to use to measure the bandwidth
nbpackets = 2
bandwidth = 0
while True:
    bandwidth = 0
    file = open("frames.txt")
    ts = []

    for line in (file.readlines() [-nbpackets:]): 
        ts.append(line.split('(')[1].split(')')[0])
        
    delta = float(ts[len(ts)-1]) - float(ts[0])
    bandwidth = psize*nbpackets/delta

    now = time.time()
    lastMsg = now - float(ts[-1])

    print("Bandwidth:"+str(bandwidth) + " B/s")   
    print("Last message " + str(lastMsg)+" secs ago") 
    
    time.sleep(1)
