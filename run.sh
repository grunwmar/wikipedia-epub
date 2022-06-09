#!/bin/bash


clear
source venv/bin/activate

URL_LIST="./cfg/url_list"

export WD_URL_LIST=$URL_LIST

vim $URL_LIST

python3 __main__.py
