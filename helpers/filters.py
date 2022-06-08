#!/usr/bin/python
import sys
import urllib.request
import urllib.parse
import re
import logging

log = logging.getLogger()


def perform_html_trim(soup):

    for style in soup.find_all('style'):
        style.extract()

    for img in soup.find_all('img'):
        del img['data-file-height']
        del img['data-file-width']
        del img['decoding']
        del img['srcset']

    for div in soup.find_all('div'):
        del div['style']

    for table in soup.find_all('table'):
        del table['style']

    for a in soup.find_all('a'):
        a.unwrap()

    for math in soup.find_all('math'):
        math.extract()

    for mathml in soup.find_all('span', {'class': 'mwe-math-mathml-inline mwe-math-mathml-a11y'}):
        mathml.extract()    

    for edit_section in soup.find_all('span', {'class': 'mw-editsection'}):
        edit_section.extract()

    for auth_control in soup.find_all('div', {'class': 'navbox'}):
        auth_control.extract()

    for toc in soup.find_all('div', {'class': 'toc'}):
        toc.extract()

    for div_col in soup.find_all('div', {'class': 'div-col'}):
        div_col.extract()

    for span_see_also in soup.find_all('span', {'id': 'See_also'}):
        span_see_also.parent.extract()

    for metadata in soup.find_all('table', {'class': 'metadata'}):
        metadata.extract()

    for mbox_small in soup.find_all('table', {'class': 'mbox-small'}):
        mbox_small.extract()


def _lang_filter_yiddish(string):
    substitute_list = [
        ["וו", "װ"],
        ["וי", "ױ"],
        ["יי", "ײ"],
        ["ײַ", "ײַ"],
        ["יִ", "יִ"],
    ]
    for s in substitute_list:
        subst_regx = re.compile("{}".format(s[0]), 0)
        string = subst_regx.sub(s[1], string)
    return string

_LANG_FILTERS = {
    "yi": _lang_filter_yiddish,
    "en": _lang_filter_yiddish,
}


def lang_filter(lang, string):
    lang_filter_f = _LANG_FILTERS.get(lang.lower())
    if lang_filter_f is not None:
        return lang_filter_f(string)
    else:
        return string
