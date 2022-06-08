#!/bin/bash
CALIBRE=$(which "calibre")
PYVENV=$(which)

if [ -z $CALIBRE ]; then
    echo -n "Program 'ebook-converter' is not present. Do you want to instal 'calibre' package? "
    read ANSWER
    if [[ $ANSWER = 'y' ]]; then
	    sudo apt-get install calibre
        else
        exit
    fi
fi

if [ -z $PYVENV ]; then
    echo -n "Program 'python3-venv' is not present. Do you want to instal 'python3-venv' package? "
    read ANSWER
    if [[ $ANSWER = 'y' ]]; then
	    sudo apt-get install python3-venv
        else
        exit
    fi
fi

python3 -m venv ./venv

source ./venv/bin/activate
pip install -r requirements.txt
