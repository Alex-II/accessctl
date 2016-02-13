#!/usr/bin/env python
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
from array import array
import base64
import datetime
continue_reading = True


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    LockDoor()
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

accessLogFilenameSuccess = "/accessctl/accessLogSuccess.txt"
accessLogFilenameFail    = "/accessctl/accessLogFail.txt"
runLog = "/accessctl/run.log"

with open(runLog, 'a') as accessFile:
        accessFile.write(str(datetime.datetime.now()) + ":" + "Started.." + "\n" )



def LogAccessSuccess(card):
        with open(accessLogFilenameSuccess, 'a') as accessFile:
                accessFile.write(str(datetime.datetime.now()) + ":" + str(card) + "\n" )
def LogAccessFail(card):
        with open(accessLogFilenameFail, 'a') as accessFile:
                accessFile.write(str(datetime.datetime.now()) + ":" + str(card)  + "\n")

def UnlockDoor():
        GPIO.output(11, 1)

def LockDoor():
        GPIO.output(11, 0)

#Read list of accepted cards - expecting it to be in the same dir

trustedCardsFileName = "/accessctl/trustedCards.txt"
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
totalOpenTime = 1.5

doorLock = True;
lastValidUnlockTime = 0;

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    print '.'

    #maybe it's time to close the door
    if(time.time() > lastValidUnlockTime + totalOpenTime):
        print "Door Locked"
        LockDoor()


    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

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

        #print(  base64.urlsafe_b64encode(a.tostring()).replace('=','')  )





