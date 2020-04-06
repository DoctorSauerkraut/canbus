#  CAN Bus Key manager

import json

from exceptions import UnauthorizedAccessToKey
import config


class KeyManager:
    """
    Key loading and attributing depending on node groups
    """
    # Node groups keymap
    keyMap = {}

    def __init__(self):
        self.keyMap = self.loadKeyMap()

    def getKeyMap(self):
        return self.keyMap

    def loadKey(self, idNode, idGroup):
        """
        Checks the group keys corresponding to the given node
        """

        # if(self.isNodeMemberOfGroup(idNode, idGroup)):
        return self.loadKeyFile(idGroup)
        # else:
        #    raise UnauthorizedAccessToKey(idNode, idGroup)

    def loadKeyMap(self):
        """
        Loads the keymap of the bus
        """
        f = open(config.KEYSPATH+"keymap", "r")
        return json.load(f)

    def isNodeMemberOfGroup(self, idNode, idGroup):
        """
        Checks if a node is a member of the given group
        """
        if(idNode in self.keyMap[str(idGroup)]):
            return True
        return False

    def loadKeyFile(self, idKey):
        """
        Loads a specified key file
        """
        try:
            f = open(config.KEYSPATH + str(idKey) + ".key", "r+")
            for line in f:
                return line
        except FileNotFoundError:
            print("No key file found for id:" + idKey)
