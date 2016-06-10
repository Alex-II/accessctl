### Overview


This folder contains the standalone rfid card reader.
There are 2 python scripts:
  1. Card Reader
  2. Webapp 

The Card Reader script reads the card number of the rfid cards presented to the hardware reader.
If the card number matches a list of known valid cards, the door is opened.

The Webapp script presents a webgui interface so that the list of valid cards can be identified.


### Running

Run the Card Reader script (card_reader.py) as root/with sudo: it needs to run as root because of the hardware access.

The Card Reader script will also start the Webapp script.
The Webapp script will demote itself from root to a non-root user.


### Installing


### Card Reader
The Card Reader script interfaces with the hardware rfid card reader, the MFRC522.
A user presents an rfid card to the reader and the script gets the user's card number.
The script validates the user's card number against known valid card numbers. 
Only if the card is valid is the door unlocked. 

The script loads the list of known valid cards from a file, the 'users.json' file.
The script rereads the file when it gets a signal from the Webapp script, which is responsible for updating the 'users.json' file.


#### Details

### Webapp
The Webapp script is responsible for updating the 'users.json' file.
It's a webserver that presents a standard interface that allows the add/remove/edit of member cards (and setting them to valid or invalid)
The webserver has authentication but only has one set of credentials (username/password configured in the 'webapp_settings.json' file)


#### Details
