#!/usr/bin/python
import sys
from bs4 import BeautifulSoup
from datetime import datetime as dt
import re
import json
import os
import urllib.request
import urllib.parse
import shutil
from helpers import parse_url, wikipedia_api, download_image, export_destination, make_envelope
from helpers import get_language_name
from helpers.filters import perform_html_trim, lang_filter, safe_filename
import logging
import logging as log
import os
import traceback


log = logging.getLogger()


NOW = dt.now()
TIMESTAMP = NOW.strftime('%Y%m%d%H%M%S%f')
EXPORT_DIR = export_destination()
RTL_LANGUAGES = ['he', 'yi', 'ar']


def process(run_name, input_url, count):

    language, title = parse_url(input_url)

    if language is None or title is None:
        log.critical(f'Invalid result of parsing language={language}, title={title}  <== invalid parse result')
        return 1
    
    title_ = urllib.parse.unquote(title)

    print(f"[\033[1m\033[36;1m{count: >3}\033[0m]\033[32;1m {language} \033[30;1m\033[42m {title_} \033[0m \n")

    log.info(f"Downloading article '{title_}' in with language code '{language}' ")


    title, text, id = wikipedia_api(title, language)

    if title is None or text is None:
        if text is not None:
            text = '<str>'
        log.critical(f'Invalid result from Wikipedia API title={title}, text={text} <== invalid API response')
        return 1

    soup = BeautifulSoup(text, 'html.parser')
    dir_name = f"./tmp/TMP_{id}"
    os.mkdir(dir_name)

    perform_html_trim(soup)
    
    images = soup.find_all('img')
    images_number = len(images)
    images_downloaded = 0
    images_failed = 0

    log.debug(f'** downloading {images_number} images...')

    for n, img in enumerate(images, start=1):
        d = download_image(img, dir_name, n)
        if d:
            images_downloaded +=1
        else:
            images_failed += 1

    log.debug(f'** downloaded: {images_downloaded}, failed: {images_failed}')

    language_name_tuple = get_language_name(language)

    direction = 'ltr'
    if language in RTL_LANGUAGES:
        direction = 'rtl'

    body = str(soup)
    html_envelope = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{language}" lang="{language}" dir="{direction}">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<link rel="stylesheet" type="text/css" href="document_style.css"/>
<title>{title}</title>
<script>

</script>
</head>
<body>
    <h1>{lang_filter(language, title)}</h1>
    {lang_filter(language, body)}
</body>
</html>
    """

    with open('document_style.css', 'r') as style_file:
        with open(os.path.join(dir_name, 'document_style.css'), 'w') as new_style_file:
            new_style_file.write(style_file.read())
    
    doc_path = os.path.join(dir_name, 'document.xhtml')
    epub_name = safe_filename(title)

    with open(doc_path, 'w') as doc_file:
        doc_file.write(lang_filter(language, html_envelope))

    log.debug('Converting to EPUB file...')

    if run_name != "!x-none":
        NAMED_DIR = os.path.join(export_destination(), run_name)

        if not os.path.isdir(NAMED_DIR):
            os.mkdir(NAMED_DIR)

        EXPORT_DIR = NAMED_DIR

    filename_lang = f'{language.upper()}_{epub_name}'
    run_name_path = os.path.join(run_name, filename_lang)
    export_path = os.path.join(EXPORT_DIR, filename_lang)
    
    if language_name_tuple[0].lower() == language_name_tuple[1].lower():
        lang_a = f'{language_name_tuple[1]}; '.split('; ')[0]
        language_name = f'{lang_a}'
    else:
        lang_a = f'{language_name_tuple[0]}; '.split('; ')[0]
        lang_b = f'{language_name_tuple[1]}; '.split('; ')[0]
        language_name = f'{lang_a} ({lang_b})'
    try:
        conversion = os.system(f'bash make_epub.sh "{doc_path}" "{export_path}" "{language}" "{title}" "{input_url}" "{language_name}"')
        with open("downloads.txt", "a") as down_file:
            down_file.write(input_url + "\n")
            
    except Exception as e:
        log.critical('Error', e)
    
    log.info('Converted')
    
    shutil.rmtree(dir_name)
    log.info(f'Article "{title.upper()}" saved as "{urllib.parse.unquote(run_name_path)}.epub"')
    log.debug(f'-> "{urllib.parse.unquote(export_path)}.epub"')
    return 0


def run(run_name, input_url, count):
    try:
        process(run_name, input_url, count)
    except Exception as e:
        err = f"Error: ",  str(e)
        log.exception('Error ' + str(e))
    log.info("Exit \n\n")

