# User-defined exceptions for CAN Bus simulator


class UnauthorizedAccessToKey(RuntimeError):
    def __init__(self, idNode, idGroup):
        print("ERROR : Node " + str(idNode)
              + " is not member of group " + str(idGroup))
        exit
