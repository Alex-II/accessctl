### Overview


This folder contains the standalone rfid card reader.
There are 2 python scripts:
  1. Card Reader
  2. Webapp 

The Card Reader script interfaces with the hardware rfid card reader, the MFRC522.
A user presents an rfid card to the reader and the script gets the user's card number.
The script compares the user's card number against known valid card numbers.

Only if the card is valid is the door unlocked. 

The script loads the list of known valid cards from a file.
The script rereads the file containing the list of known valid cards when it gets a signal from the Webapp script
The Webapp script is the one that updates said file and then notifies the Card Reader script so that it can reread it.



### Card Reader


### Webapp
