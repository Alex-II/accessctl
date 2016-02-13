import logging
import traceback

from door_controller import Door
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
    door = Door()

    door.communication = get_comms()
    door.lock = get_lock()
    door.reader = get_card_reader()

    door.reader.read_callback(door.read)

    door.reader.listen()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        trace_stack = traceback.format_exc()
        logger.critical("Unrecoverable error has occurred: {0}".format(str(e)))
        logger.critical("{0}".format(trace_stack))