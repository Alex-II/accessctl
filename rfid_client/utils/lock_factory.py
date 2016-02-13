import logging

from utils.factory_utils import get_availble_drivers, get_driver_identifier, load_driver
logger = logging.getLogger('Controller')


def setup_logging():
    logger_driver = logging.getLogger('Lock')
    logger_driver.propagate = False
    ch = logging.StreamHandler()
    log_format = '%(asctime)-15s [%(threadName)-10s] [%(levelname)-8s] %(name)s - %(message)s'
    formatter = logging.Formatter(log_format)
    ch.setFormatter(formatter)
    logger_driver.addHandler(ch)
    logger_driver.setLevel(level=logging.DEBUG)


def get_lock():
    logger.info("* Loading Lock Driver *")
    setup_logging()
    available_readers_file = 'configs/available_locks'
    available_readers = get_availble_drivers(available_readers_file)

    identifier_file = "configs/lock.txt"
    reader_identifier = get_driver_identifier(identifier_file)

    reader = load_driver(available_readers, reader_identifier)
    return reader


