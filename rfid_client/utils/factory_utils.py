import logging, os, imp

def load_driver(available_drivers, driver_id):
    '''
    Excepts a dict of available drivers ( {'<driver_id>':'<driver_location'>} )
    Expects a string for the driver_id
    Looks up the driver location, loads up the source file as a module
    Returns an instance of the class Driver (the loaded module needs to ensure the Driver class is available)

    :param available_drivers: dict
    :param driver_id: str
    :return: instance
    '''

    if not available_drivers.has_key(driver_id):
        raise KeyError("The driver id '{driver_id}' cannot be found in the list of available drivers".format(**locals()))

    filepath_relative = available_drivers[driver_id]
    logging.debug("Resolving absolute path of '{filepath_relative}'".format(**locals()))

    filepath = os.path.abspath(filepath_relative)

    driver_name = os.path.basename(filepath)
    if '.' in driver_name:
        driver_name = ".".join(driver_name.split(".")[:-1])

    logging.debug("Loading driver '{driver_name}' located at '{filepath}'".format(**locals()))

    module = imp.load_source('driver', filepath)

    return module.Driver()

def get_availble_drivers(available_driers_file):
    '''
    Excepts a path to a file containing a newline-separated list of available drivers and their locations on the filesysem
    On every line expecting "<driver_id>,<driver_relative_path>"
    Example of file contents:

        MFRC522, card_reader_drivers/MFRC522_wrapper.py
        FF54, card_reader_drivers/FF54.py #we can have a comment here

    Returns a dict of {'<driver_id>':'<driver_location'>}

    :param available_driers_file: str
    :return: dict
    '''
    logging.debug("Loading up list of available drivers from file '{available_driers_file}'".format(**locals()))

    drivers = {}
    with open(available_driers_file, 'r') as fd:
        lines = fd.readlines()
        for line in lines:
            line = line.strip("\n")
            line_no_comments = line.split("#")[0]

            if ',' in line_no_comments:
                logging.debug('Parsing line: "{line}" '.format(**locals()))

                identifier = line_no_comments.split(",")[0].strip()
                driver_location = line_no_comments.split(",")[1].strip()

                logging.debug("  Parsed '{identifier}' at '{driver_location}'".format(**locals()))
                if len(identifier) == 0:
                    logging.warning(  "Driver identifier for this line is empty")

                if not os.path.isfile(driver_location):
                    logging.warning("  Driver location on this line cannot be found on filesystem")

                drivers[identifier] = driver_location
    return drivers

def get_driver_identifier(identifier_file):
    '''
    Expects a path to a file containing the id (name) of the driver we wish to load

    :param identifier_file: str
    :return: str
    '''
    logging.debug("Reading file '{identifier_file}' to identify what driver to load".format(**locals()))
    with open(identifier_file,'r') as fd:
        identifier = fd.read()
        identifier.strip("\n").strip()
    logging.debug("Reader ID specified in file: '{identifier}'".format(**locals()))
    return identifier