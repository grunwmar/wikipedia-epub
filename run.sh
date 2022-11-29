#!/bin/bash
clear
source venv/bin/activate

URL_LIST="./cfg/url_list"

export WD_ARTICLE_INDEX=1

vim $URL_LIST

python3 expand_url.py "$URL_LIST"

RAW_STRING=$(sed -n '1{/^@/p};q' $URL_LIST)
RUN_TITLE="!x-none"

if ! [ -z "$RAW_STRING" ]
    then
    RUN_TITLE="${RAW_STRING:1}"
fi

FIRST=1
while read row; do
    if ! [ $FIRST = 1 ];
        then

        if ! [ -z $row ]
            then
            echo -e " --------------------------- "
            export WD_ARTICLE_URL=$row
            export WD_RUN_TITLE=$RUN_TITLE
            python3 __main__.py
            echo ""
        fi
    fi

    FIRST=0

done <"./cfg/url_list"
export WD_ARTICLE_INDEX=1

echo " ... "
read x
