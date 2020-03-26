#!/bin/sh

# CAN Bus Simulator Monitor
LOOP=0
CANNETWORK=192.168.2
HDR="CAN BUS SIMULATION MONITOR\n##########################"

while [ $LOOP -ne 1 ]
	do
		STR=""
		for HOSTNUM in 1 2 3 4 5 
			do
				ping -c 1 $CANNETWORK.1$HOSTNUM > /dev/null
				if [ $? -eq 0 ]; then
					STR="$STR$CANNETWORK.1$HOSTNUM --- ALIVE\n"
				else
					STR="$STR$CANNETWORK.1$HOSTNUM --- DEAD\n"
				fi
			done
		clear
		echo $HDR
		date
		echo $STR
	done
