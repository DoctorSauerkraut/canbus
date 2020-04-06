# Key generation utility

import random
import json

import config


class KeyGen:
    """
    Key Generation class
    Keymap generation and key managing for all the bus
    """

    # Keymap to define node groups
    keyMap = {}

    def genKey(self, idKey):
        """
        Generates a new key file for a node
        """
        f = open(config.KEYSPATH + str(idKey) + ".key", "w")
        f.write("0123456789")
        f.close()

    def generateMsgMap(self, totalGroups):
        """
        Generates a random association between message ids and group keys
        """
        return True

    def generateKeyMap(self, totalNodes, totalGroups):
        """
        Generates a random key map to determine which node can communicate
        with which
        """
        # Used to determine if each node belongs to, at least, one group
        attributedNodes = []

        for g in range(0, totalGroups):
            self.keyMap[str(g)] = []
            self.genKey(g)

            for j in range(0, totalNodes):
                r = random.randint(0, 2)
                if(r == 0):
                    self.keyMap[str(g)].append(j)
                    if(j not in attributedNodes):
                        attributedNodes.append(j)

            # Assign all non assigned nodes
            if(g == totalGroups - 1):
                for n in range(0, totalNodes):
                    if(n not in attributedNodes):
                        group = random.randint(0, totalGroups-1)
                        self.keyMap[str(group)].append(n)

        f = open(config.KEYSPATH + "keymap", "w")
        json.dump(self.keyMap, f)

    def checkKeyMap(self, totalNodes, totalGroups):
        """
        Displays all associated groups for each node (debug purposes)
        """
        toPrint = ""
        for n in range(0, totalNodes):
            toPrint = "Node "+str(n)+" :"
            for g in range(0, totalGroups):
                if(n in self.keyMap[str(g)]):
                    toPrint = toPrint + " " + str(g)

            print(toPrint)


if __name__ == "__main__":
    k = KeyGen()

    with open(config.CONFIGPATH + "config.json", 'r') as f:
        params = json.load(f)

    totalNodes = params["totalNodes"]
    totalGroups = params["groups"]

    k.generateKeyMap(totalNodes, totalGroups)

    # Node assignation verification
    k.checkKeyMap(totalNodes, totalGroups)
