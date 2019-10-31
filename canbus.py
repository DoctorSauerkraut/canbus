import time

from can import *
from can.interfaces.socketcan.socketcan import SocketcanBus

class CanBUS(SocketcanBus):
    msgOnBus = []
    
    def __init__(self, channel, can_filters=None, **config):
        super().__init__(channel, can_filters, config)