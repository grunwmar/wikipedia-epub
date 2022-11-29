import requests
import json
import urllib.request
import urllib.parse
import re
import sys


def parse_url(url):
    expr = re.compile(r'https?\:\/\/([a-z\-]+)\.wikipedia\.org\/wiki\/(.+)')
    result = expr.findall(url)
    if len(result) == 1:
        if result[0][0] != '' or result[0][1] != '':
            return result[0]
    return None, None


def wikipedia_api_langlings(title, language="en"):
    try:
        url=f"https://{language}.wikipedia.org/w/api.php?action=parse&page={title}&format=json&formatversion=1"

        headers = {
             'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0',
        }

        rq = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(rq) as response:

            if response.status == 200:

                read = response.read()

                response_string = read.decode('utf-8')
                data = json.loads(response_string)

                if data.get('error') is not None:
                    return None, None, None

                title = data['parse']['title']
                text = data['parse']['text']['*']

                langlinks = data['parse']['langlinks']

                return [{'lang': i['lang'].lower(), 'url': i['url']} for i in langlinks]

            else:
                return None

    except Exception as e:
        print(e)
        return None



def get_results(url, lang_list):

    lang, title = parse_url(url)
    langlinks = wikipedia_api_langlings(title, lang)

    results = []
    for i in langlinks:
        if i.get('lang') in lang_list:
            results += [i['url']]
    print(f'Splitting {url} to: ', end='')
    langlinks_str = "\n\t * ".join(results)
    print("\n\t * " + langlinks_str)
    return results


def parse_row(row):
    expr = re.compile(r'(https?\:\/\/[a-z\-]+\.wikipedia\.org\/wiki\/.+) \:\: ((\w*\|?)*)')
    result = expr.findall(row)
    new_results = []
    for i in result:
        if len(i) > 0:
            new_results += [i[0], tuple(i[1].split('|'))]
    return new_results


def main():
    with open(sys.argv[1], 'r') as fp:
        url_list = []
        for row in fp.read().split('\n'):

            try:
                if len(row) > 0:
                    r = parse_row(row)
                    url_list += get_results(*r)
            except TypeError:
                url_list += [row]

    with open(sys.argv[1], 'w') as fp2:
        fp2.write("\n".join(url_list))


main()
