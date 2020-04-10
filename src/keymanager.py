#  CAN Bus Key manager

import json

from exceptions import UnauthorizedAccessToKey
from exceptions import NoGroupForMessage
import config


class KeyManager:
    """
    Key loading and attributing depending on node groups
    """
    # Node groups keymap
    keyMap = {}
    msgMap = {}

    def __init__(self):
        self.keyMap = self.loadKeyMap()
        self.msgMap = self.loadGroupAndMsg()

    def getKeyMap(self):
        return self.keyMap

    def loadKey(self, idNode, idGroup):
        """
        Checks the group keys corresponding to the given node
        """

        if(self.isNodeMemberOfGroup(idNode, idGroup)):
            return self.loadKeyFile(idGroup)
        else:
            raise UnauthorizedAccessToKey(idNode, idGroup)

    def loadGroupAndMsg(self):
        """
        Loads the msg/group association map
        """
        f = open(config.KEYSPATH+"msgmap", "r")
        return json.load(f)

    def getGrpIdFromMsgId(self, msgId):
        """
        Gets the group key number corresponding to the message
        """
        for g in self.msgMap.keys():
            if(msgId in self.msgMap[g]):
                return g

        raise NoGroupForMessage(msgId)

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
            f = open(config.KEYSPATH + str(idKey) + ".key", "rb")
            return f.read()
        except FileNotFoundError:
            print("No key file found for id:" + idKey)

    def getMessagesFromGroup(self, idGrp):
        """
        Returns the set of potential messages for a given group
        """
        return self.msgMap[str(idGrp)]

    def getGroupsForNode(self, nodeId):
        """
        Returns the set of available groups keys for a given node
        """
        grpList = []

        # Extract all potential groups corresponding to the node id
        for grp in self.keyMap:
            if nodeId in self.keyMap[grp]:
                grpList.append(grp)

        return grpList
