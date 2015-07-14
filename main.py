#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
from array import array
import datetime


#################
####Config
#################
LATCH_PIN = 11

accessLogFilenameSuccess = "accessLogSuccess.txt"
accessLogFilenameFail = "accessLogFail.txt"
trustedCardsFileName = "trustedCards.txt"

#################
#Mos Def
#################

def LogAccessSuccess(cID):
    with open(accessLogFilenameSuccess, 'a') as accessFile:
        accessFile.write(str(datetime.datetime.now()) + ":" + str(cID) + "\n")
def LogAccessFail(cID):
    with open(accessLogFilenameFail, 'a') as accessFile:
        accessFile.write(str(datetime.datetime.now()) + ":" + str(cID)  + "\n")

def UnlockDoor():
    GPIO.output(LATCH_PIN, 1)

def LockDoor():
    GPIO.output(LATCH_PIN, 0)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    print "Ctrl+C captured, ending read."
    continue_reading = False
    LockDoor()
    GPIO.cleanup()


#################
## Main
#################
continue_reading = True

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LATCH_PIN, GPIO.OUT)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

#Read list of accepted cards - expecting it to be in the same dir

trustedCards = []
with open(trustedCardsFileName, 'r') as cardsFile:
    lines = cardsFile.readlines()
    for line in lines:
        #map isn't working, wtf
        card = line.split(",")
        fpCard = []
        for c in card:
            c = str.strip(c)
            c = int(c)
            fpCard.append(c)
        trustedCards.append(fpCard)

#how much total time should the door be open upon correct card
totalOpenTime = 15

doorLock = True
lastValidUnlockTime = 0

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    print '.'

    #maybe it's time to close the door
    if time.time() > lastValidUnlockTime + totalOpenTime:
        print "Door Locked"
        LockDoor()


    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        a = array('B')
        a.fromlist(uid[:-1])
        print "Card Read:" + str(uid)
        cardValid = False
        for card in trustedCards:
            if (card == uid):
                print "Matches"
                UnlockDoor()
                lastValidUnlockTime = time.time()
                LogAccessSuccess(uid)
                cardValid = True

            else:
                print "No Match"

        if(cardValid == False):
            LogAccessFail(uid)


print "Exiting normally :)"





