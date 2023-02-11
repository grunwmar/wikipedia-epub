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
from helpers.filters import perform_html_trim, lang_filter
import logging
import logging as log
import os
import time

CONN_CONFIG = {
    "ImageDownloadPause": 0.5,
    "ImageDownloadVerbose": False,
    "MainInitPause": 1,
    "OutputFormat": "epub"
}

try:
    with open('./cfg/connection.json') as cf:
        CONN_CONFIG = json.load(cf)
except:
    ...


log_format_string_F = '[%(asctime)s] %(levelname)-8s  %(message)s'
log_format_string_C = '[\033[1m%(asctime)s\033[0m] \033[36m%(levelname)-8s\033[0m  %(message)s'
logging.basicConfig(
     filename='logger.txt',
     level=logging.DEBUG,
     format= log_format_string_F,
     datefmt='%Y-%m-%d %H:%M:%S'
 )


# set up logging to console
console = log.StreamHandler()
console.setLevel(logging.INFO)

# set a format which is simpler for console use
formatter = logging.Formatter(log_format_string_C)
console.setFormatter(formatter)

# add the handler to the root logger
log.getLogger('').addHandler(console)


NOW = dt.now()
TIMESTAMP = NOW.strftime('%Y%m%d%H%M%S%f')
TIMESTAMP_DL = NOW.strftime('%Y-%m-%d %H:%M:%S')
EXPORT_DIR = export_destination()
RTL_LANGUAGES = ['he', 'yi', 'ar']

def main():
    input_url = os.environ.get('WD_ARTICLE_URL')
    run_title = os.environ.get('WD_RUN_TITLE')

    language, title = parse_url(input_url)

    if language is None or title is None:
        log.critical(f'Invalid result of parsing language={language}, title={title}  <== invalid parse result')
        return 1

    title_ = urllib.parse.unquote(title)

    print(f" -> \033[1m\033[34m{language}\033[0m:\033[1m\033[32m{title_}\033[0m \n")

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
        try:
            if CONN_CONFIG['ImageDownloadVerbose']:
                print(f"#{n} - {img}")
            d = download_image(img, dir_name, n)
            if d:
                images_downloaded +=1
            else:
                images_failed += 1
        except Exception as e:
            images_failed += 1
            log.critical(f'Image could not be downloaded. <{e}>')
        time.sleep(CONN_CONFIG['ImageDownloadPause'])

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
    epub_name = title.replace(' ', '_').replace(':', '-').replace('/', '_').replace('\\', '_')

    with open(doc_path, 'w') as doc_file:
        doc_file.write(lang_filter(language, html_envelope))

    log.debug('Converting to EPUB file...')

    if run_title != "!x-none":
        NAMED_DIR = os.path.join(export_destination(), run_title)

        if not os.path.isdir(NAMED_DIR):
            os.mkdir(NAMED_DIR)

        EXPORT_DIR = NAMED_DIR

    export_path = os.path.join(EXPORT_DIR, f'{language.upper()}_{epub_name}')
    if language_name_tuple[0].lower() == language_name_tuple[1].lower():
        lang_a = f'{language_name_tuple[1]}; '.split('; ')[0]
        language_name = f'{lang_a}'
    else:
        lang_a = f'{language_name_tuple[0]}; '.split('; ')[0]
        lang_b = f'{language_name_tuple[1]}; '.split('; ')[0]
        language_name = f'{lang_a} ({lang_b})'
    try:
        output_fmt = CONN_CONFIG['OutputFormat'].lower()
        conversion = os.system(f'bash make_{output_fmt}_.sh "{doc_path}" "{export_path}" "{language}" "{title}" "{input_url}" "{language_name}"')
        with open("downloads.txt", "a") as down_file:
            down_file.write(input_url + f" # {TIMESTAMP_DL}\n")

    except Exception as e:
        log.critical('Error', e)

    log.info('Converted')

    shutil.rmtree(dir_name)
    log.info(f'Article "{title.upper()}" saved as "{urllib.parse.unquote(export_path)}.epub"')
    return 0


if __name__ == '__main__':
    try:
        main()
        time.sleep(CONN_CONFIG['MainInitPause'])
    except Exception as e:
        err = f"Error: ",  str(e)
        log.critical('Error ' + str(e))
    log.info("Exit \n\n")
