import logging
import traceback

from controller import Controller
from utils.comms_factory import get_comms
from utils.lock_factory import get_lock
from utils.reader_factory import get_card_reader

logger = logging.getLogger('Controller')
logger.propagate = False
ch = logging.StreamHandler()
log_format = '%(asctime)-15s [%(threadName)-10s] [%(levelname)-8s] %(name)s - %(message)s'
formatter = logging.Formatter(log_format)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(level=logging.DEBUG)


def main():
    #Controller class manipulates the lock, gets called by the reader and initiates communicate with the server
    controller = Controller()

    controller.communication = get_comms()
    controller.lock = get_lock()
    controller.reader = get_card_reader()

    #Registring the Controller method we want to be called when a card is read
    controller.reader.read_callback(controller.read)

    controller.reader.listen()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        trace_stack = traceback.format_exc()
        logger.critical("Unrecoverable error has occurred: {0}".format(str(e)))
        logger.critical("{0}".format(trace_stack))