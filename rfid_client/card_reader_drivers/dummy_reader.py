import logging
from random import randint
from time import sleep
import threading


#Dummy reader, it sleeps and calls the Controller with several shitty card IDs (to kinda-simulate quick successive reads)
class Reader():
    def read_callback(self, callback):
        self.callback = callback
        self.logger = logging.getLogger('Reader')

    def listen(self):
        self.logger.debug("* Dummy Read Driver - will send some whatver id after sleeping a while")
        card_ids = ['11','22','33']

        card_read = card_ids[randint(0,len(card_ids)-1)]

        sleepy_time  = 0.150

        self.logger.debug("Sleeping for {sleepy_time} milliseconds".format(**locals()))
        sleep(sleepy_time)

        for card in card_ids:
            thr = threading.Thread(target=self.callback, args=(card, ), kwargs={})
            thr.start()


Driver = Reader