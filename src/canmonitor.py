import threading
import time
from os import system

from canbus import CanBUS
from can import Notifier
from msglistener import MsgListener

from logger import Logger
""" Monitors the bus state and used bandwidth """


class CanMonitorThread(threading.Thread):
    bus = None
    recMon = None

    def __init__(self, bus_):
        threading.Thread.__init__(self)
        self.bus = bus_
        print("Initializing monitor")
        self.recMon = CanMonitor(self.bus)

    def run(self):
        print("Setting up monitor notifier")
        Notifier(self.bus, [MsgListener(self.recMon)])

    def getMonitor(self):
        return self.recMon


class CanMonitor():
    bus = None
    receivedTimestamps = []

    def __init__(self, bus_):
        self.bus = bus

    def receive(self, msg):
        """ On message reception """
        size = 44
        if(msg.is_extended_id):
            size = size + 20

        size = size+len(msg.data)*8

        self.receivedTimestamps = self.receivedTimestamps + [(msg.timestamp, size)]

        if(len(self.receivedTimestamps) > 10000):
            self.receivedTimestamps.pop(0)

        


    def getTimestamps(self):
        return self.receivedTimestamps


if __name__ == "__main__":
    Logger.log("OK")
    bus = CanBUS(interface='socketcan',
                 channel="can0",
                 can_filters="",
                 receive_own_messages=True)
    logger = Logger()

    monitor = CanMonitorThread(bus)
    Logger.log("Starting monitor")
    monitor.start()

    while(1):
        timestamps = monitor.getMonitor().getTimestamps()

        if(len(timestamps) > 1):   
            # Computing the average bit rate consumption 
            currentTime = time.time()
            # Packets transmitted on the last 5s

            size = 0
            for i in range(0, len(timestamps)):
                if (timestamps[i][0] > currentTime-5):
                    size = size + timestamps[i][1]

            bitrate = size/(5*8)
            system("clear")
            Logger.log("Bitrate:"+str(bitrate)+" B/s")
            time.sleep(1)
