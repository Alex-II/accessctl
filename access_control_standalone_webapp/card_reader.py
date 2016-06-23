#!/usr/bin/env python
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
from array import array
import base64
import os
import datetime
import subprocess
import json
import fcntl
import errno
import code
import logging
import sys
    

log = logging.getLogger("Card Reader Module")
cards_read_log = logging.getLogger("Cards Scanned")

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    LockDoor()
    GPIO.cleanup()

def UnlockDoor():
        GPIO.output(11, 1)

def LockDoor():
        GPIO.output(11, 0)
        
def child_process_has_signaled(pipe_read):

    try:
        buffer = pipe_read.read()
    except IOError as exc:
      if exc.errno == errno.EAGAIN:
         return False

    if buffer:
        return True
    else:
        return False

        
def is_card_valid(card_number, users):
    for user in users:
        if user['card_number'] == card_number and user['active'] == True:
            print "Name: ", user['name']
            return True
        
    return False

#total_open_time: how much time to keep the door open if the card was correct
def main_loop(total_open_time,  loop_sleep_seconds, users):
    lastValidUnlockTime = 0; # keeping track of last time we detected a correct rfid card (so we know how much time to wait)
    
        
    MIFAREReader = MFRC522.MFRC522() # Create an object of the class MFRC522
    
    pipe_read = spawn_webapp()
    
    # This loop keeps checking for rfid cards. If one is near it will get the UID and authenticate
    while continue_reading:
        print '.'
        if child_process_has_signaled(pipe_read):
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FILE CHANGED"
            users = read_users_file()
        else:
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> file not changed"
    
        #maybe it's time to close the door
        if(time.time() > lastValidUnlockTime + total_open_time):
            print "Door Locked"
            LockDoor()
        else:
            print "Door still unlocked"
            
        # Scan for cards
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print "Card detected"

        # Get the UID of the card
        (status,card_number_list) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            card_number = "".join(str(x) for x in card_number_list)
            print "Card Read:" + str(card_number)
            if is_card_valid(card_number, users):
                lastValidUnlockTime = time.time()
                print "Card valid"
                UnlockDoor()
            else:
                print "Card not valid"
            
            
            
def set_logging(log_level):
    #normal logging
    if log_level:
        log.setLevel(log_level)
        ch = logging.FileHandler("card_reader.log")
        ch.setLevel(log_level)
        
        log_format = '%(asctime)-15s - %(levelname)-5s - %(message)s'
        formatter = logging.Formatter(log_format)
        ch.setFormatter(formatter)
        log.addHandler(ch)
        
    #loggin specifically for what cards were scanned, unconditional logging
    cards_read_log.setLevel(logging.INFO)
    dh = logging.FileHandler("card_scanned.log")
    dh.setLevel(logging.INFO)
    
    log_format_cards = '%(created),%(message)s'
    formatter = logging.Formatter(log_format_cards)
    dh.setFormatter(formatter)
    cards_read_log.addHandler(dh)
        
            
def read_config_file(filename = "card_reader_settings.json"):
    with open(filename, 'r') as fd:
        config = json.loads(fd.read())
        
    if not "loop_sleep_seconds" in config:
            raise ValueError('Expecting key "loop_sleep_seconds" in the json file')
    else:
        loop_sleep_seconds = float(config['loop_sleep_seconds'])
        
    if not "door_unlocked_seconds" in config:
            raise ValueError('Expecting key "door_unlocked_seconds" in the json file')
    else:
        door_unlocked_seconds = float(config['door_unlocked_seconds'])
        
    if not "log_level" in config:
            raise ValueError('Expecting key "log_level" in the json file')
    else:
        door_unlocked_seconds = config['log_level']
        if door_unlocked_seconds.upper() == "DEBUG":
            set_logging(logging.DEBUG)
        elif door_unlocked_seconds.upper() == "INFO":
            set_logging(logging.INFO)
        elif door_unlocked_seconds.upper() == "NONE":
            set_logging(None)
        else:
            raise ValueError('Expecting key "log_level" to be set to "DEBUG", "INFO" or "NONE"')
        
    return (loop_sleep_seconds, door_unlocked_seconds)
            
def spawn_webapp():
    read_pipe_number, write_pipe_number = os.pipe() 
    
    
    
    fd = os.fdopen(read_pipe_number ,'r', 0)
    fl = fcntl.fcntl(fd.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(fd.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    command = ["/usr/bin/python", "-u", "webapp.py", "--pipe", str(write_pipe_number)] #starting the webserver
    subprocess.Popen(command)
    
    return fd

def read_users_file(filename = 'users.json'):
    if os.path.getsize(filename) == 0:
            users = []

    else:
        with open(filename, 'r') as fd:
            users = json.loads(fd.read())
            
        for user in users:
            if not "name" in user:
                raise ValueError('Expecting key "name" for each user in the users json file')
                
            if not "card_number" in user:
                raise ValueError('Expecting key "card_number" for each user in the users json file')
            
            if not "active" in user:
                raise ValueError('Expecting key "active" for each user in the users json file')
                
            if not type(user['active']) is bool:
                raise ValueError('Expecting key "active" to be of type bool for user {0}'.format(user['name']))

    return users 
    
if __name__ == '__main__':
    # Capture SIGINT
    signal.signal(signal.SIGINT, end_read)

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)

    global continue_reading #will be changed from the callback
    continue_reading = True
    
    
    
    (loop_sleep_seconds, door_unlocked_seconds) = read_config_file()
    users                                       = read_users_file()
    
    main_loop(total_open_time = door_unlocked_seconds, loop_sleep_seconds = loop_sleep_seconds, users = users)
    