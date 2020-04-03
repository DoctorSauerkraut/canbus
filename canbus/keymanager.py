#  CAN Bus Key manager


class KeyManager:

    def loadKey(self):
        f = open("config/file.key", "r+")
        for line in f:
            return line
