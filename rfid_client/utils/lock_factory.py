import logging

from utils.factory_utils import get_availble_drivers, get_driver_identifier, load_driver

def get_lock():
    logging.info("* Loading Lock Driver *")

    available_readers_file = 'configs/available_locks'
    available_readers = get_availble_drivers(available_readers_file)

    identifier_file = "configs/lock.txt"
    reader_identifier = get_driver_identifier(identifier_file)

    reader = load_driver(available_readers, reader_identifier)
    return reader


