#!/bin/bash

clear
source venv/bin/activate


URL_LIST="./cfg/url_list"

export WD_URL_LIST=$URL_LIST


if [ "$1" = "-n" ]; then
    echo "" > $URL_LIST
fi

vim $URL_LIST

python3 __main__.py

echo ""
echo "..."
read quit
