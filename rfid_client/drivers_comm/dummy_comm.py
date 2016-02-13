from random import randint
import logging



class Comm():
    def __init__(self):

        self.logger = logging.getLogger('Comms')
        self.logger.debug("  > Dummy Comm Driver - 50/50 of server accepting")

    def get_permission(self, id):
        if (randint(1,2) % 2):
            self.logger.debug("Open the door")
            return Comm.Reply(valid=True, allow=True, message="open wide")
        else:
            self.logger.debug("Don't open the door. We don't like that guy/girl")
            return Comm.Reply(valid=True, allow=False, message="open wide")

    class Reply:
        def __init__(self, valid, allow, message):
            self.valid = valid
            self.allow = allow
            self.message = message

Driver = Comm