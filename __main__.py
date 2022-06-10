import os
import re
import logging
import logging as log
import download
import time
from datetime import datetime as dt

NOW = dt.now()
TIMESTAMP = NOW.strftime('%Y-%m-%d %H:%M:%S')

log_format_string_F = '[%(asctime)s] %(levelname)-8s  %(message)s'
log_format_string_C = '[\033[1m%(asctime)s\033[0m] \033[36m%(levelname)-8s\033[0m  %(message)s'
logging.basicConfig(
     filename='logger.txt',
     level=logging.DEBUG, 
     format= log_format_string_F,
     datefmt='%H:%M:%S'
 )


# set up logging to console
console = log.StreamHandler()
console.setLevel(logging.INFO)

# set a format which is simpler for console use
formatter = logging.Formatter(log_format_string_C)
console.setFormatter(formatter)

# add the handler to the root logger
log.getLogger('').addHandler(console)



URL_LIST_FN = os.environ['WD_URL_LIST']
RUN_NAME = [None]



def parse_url_list(url_list_str):
	COUNT = 0
	for row in url_list_str.split('\n'):
		row = row.strip()
		if not row.startswith('#') and len(row) > 0:
			if row.startswith('@'):
				RUN_NAME[0] = row[1:]
			else:
				COUNT += 1
				download.run(RUN_NAME[0], row, COUNT)
				time.sleep(4)


def main():
	url_list = ''
	with open(URL_LIST_FN, 'r') as fp:
		url_list += fp.read()
		parse_url_list(url_list)

	with open(URL_LIST_FN + '.downloaded', 'a') as fp:
		fp.write(f'\n# [{TIMESTAMP}]\n')
		fp.write(url_list.strip())
		fp.write('\n')


if __name__ == '__main__':
	main()