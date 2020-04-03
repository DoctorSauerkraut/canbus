import time

from can.interfaces.socketcan.socketcan import SocketcanBus


class CanBUS(SocketcanBus):
    """
    Instantiates a socket connection to the CAN Interface
    """
    msgOnBus = []
    
    def __init__(self, channel, can_filters=None, **config):
        super().__init__(channel, can_filters, config)