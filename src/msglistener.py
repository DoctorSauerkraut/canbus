from can import Listener


class MsgListener(Listener):
    receiver = None

    def __init__(self, receiver_):
        self.receiver = receiver_

    def on_message_received(self, msg):
        self.receiver.receive(msg)