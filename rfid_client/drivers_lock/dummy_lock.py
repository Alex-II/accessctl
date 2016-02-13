import logging

#Pretend something happaened
class Lock():
    def __init__(self):
        self.logger = logging.getLogger('Lock')

    def open(self):
        self.logger.debug("Opening door")

Driver = Lock