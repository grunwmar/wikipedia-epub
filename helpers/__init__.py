#!/usr/bin/python
import sys
import re
import os
import logging 
import urllib.request
import urllib.parse
import json
import hashlib
from datetime import datetime as dt
import mimetypes
import iso639
import requests
import time

log = logging.getLogger()


def parse_url(url):
    expr = re.compile(r'https?\:\/\/([a-z\-]+)\.wikipedia\.org\/wiki\/(.+)')
    result = expr.findall(url)
    if len(result) == 1:
        if result[0][0] != '' or result[0][1] != '':
            return result[0]
    log.critical("Fatal error Url does not match")
    return None, None 


def wikipedia_api(title, language="en"):
    try:
        url=f"https://{language}.wikipedia.org/w/api.php?action=parse&prop=text&page={title}&format=json"

        headers = {
             'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
        }

        rq = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(rq) as response:
            if response.status == 200:

                read = response.read()
                
                response_string = read.decode('utf-8')
                data = json.loads(response_string)
                
                if data.get('error') is not None:
                    log.critical(f'Error in {urllib.parse.unquote(title)}', data['error'].get('info'))
                    return None, None, None

                ts = dt.now().strftime('%Y%m%d%H%M%S%f')
                h = hashlib.sha256()
                h.update(ts.encode())
                h.update(read)
                hex_string = h.hexdigest()

                title = data['parse']['title']
                text = data['parse']['text']['*']

                return title, text, hex_string
            
            else:
                log.critical(f'Returned status is {response.status} not 200.', 'bad status')
                return None, None, None

    except Exception as e:
        log.critical('Exception occured', e)
        return None, None, None


def download_image(img, dir_name, n=0):
    RE_TRIM_IMG_URL = re.compile(r'^\/\/')
    del img['aria-hidden']

    src_string = img['src']
    x = RE_TRIM_IMG_URL.findall(src_string)

    local_img_path = None

    if len(x) == 1:
        src_url = src_string.replace(x[0], 'https://')
        img['src'] = src_url

    urlopen = None
    do_next_step = False

    try:
        headers = {
             'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
        }

        rq = urllib.request.Request(img['src'], headers=headers)
    
        urlopen = urllib.request.urlopen(rq)
        do_next_step = True
            
    except ValueError as e:
        img.extract()
        log.error(f"Problem with image downloading [{img['src']}]")

    if do_next_step:
        with urlopen as response:
            if response.status == 200:
                content_type = response.info().get_content_type()
                ext = mimetypes.guess_extension(content_type)

                img_name = os.path.basename(img['src'])
                fname, fext = os.path.splitext(img_name)
                    
                if fext == '':
                    fext = ext
                    img_name = fname+fext

                img_name = f'img_{n}_{img_name}'.replace('%', '-')
                local_img_path = os.path.join(dir_name, img_name)
                with open(local_img_path, 'wb') as img_file:
                    img_file.write(response.read())
                    
                img['src'] = "./"+img_name
                return True
    # time.sleep(0.2)
    return False


def export_destination():
    with open('./cfg/export_destination') as export_dir_file:
        return export_dir_file.read().replace('\n', '')


def make_envelope(title, link, language):
    with open('./envelope.svg') as logo_file:
        return logo_file.read().format(title=title, link=link, language=language)


def get_language_name(code):
    return iso639.to_native(code), iso639.to_name(code)
