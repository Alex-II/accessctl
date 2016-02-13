import logging
import traceback

from door_controller import Door
from utils.comms_factory import get_comms
from utils.lock_factory import get_lock
from utils.reader_factory import get_card_reader


def logging_setup():
    log_format = '%(asctime)-15s [%(levelname)-8s] %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)


def main():
    logging_setup()

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
        logging.critical("Unrecoverable error has occurred: {0}".format(str(e)))
        logging.critical("{0}".format(trace_stack))