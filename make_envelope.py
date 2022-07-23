import sys

DIR="ltr"
if sys.argv[3] in ['yi', 'he', 'ar']:
    DIR="rtl"

def make(title, note):
	with open('envelope.xml', 'r') as fp:
		svg = fp.read().format(title=title, note=note, direction=DIR)

		with open(f'tmp/envelope_{title}_svg.svg', 'w') as fp:
			fp.write(svg)

make(sys.argv[1], sys.argv[2])
