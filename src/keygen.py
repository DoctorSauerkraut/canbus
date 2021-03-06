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
    msgMap = {}

    def genKey(self):
        """
        Generates a random key
        """
        return "0123456789"

    def genKeyFile(self, idKey):
        """
        Generates a new key file for a node
        """
        f = open(config.KEYSPATH + str(idKey) + ".key", "w")
        f.write(self.genKey())
        f.close()

    def generateMsgMap(self, totalGroups, totalMessages):
        """
        Generates a random association between message ids and group keys
        """
        for g in range(0, totalGroups):
            self.msgMap[str(g)] = []

        for msgCpt in range(0, totalMessages):
            grp = random.randint(0, totalGroups-1)
            self.msgMap[str(grp)].append(msgCpt)
            print("MSG " + str(msgCpt) + "\tGRP " + str(grp))
        f = open(config.KEYSPATH + "msgmap", "w")
        json.dump(self.msgMap, f)

    def generateKeyMap(self, totalNodes, totalGroups):
        """
        Generates a random key map to determine which node can communicate
        with which
        """
        # Used to determine if each node belongs to, at least, one group
        attributedNodes = []

        for g in range(0, totalGroups):
            self.keyMap[str(g)] = []
            self.genKeyFile(g)

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
    totalMessages = params["messages"]

    k.generateKeyMap(totalNodes, totalGroups)
    k.generateMsgMap(totalGroups, totalMessages)
    # Node assignation verification
    k.checkKeyMap(totalNodes, totalGroups)
