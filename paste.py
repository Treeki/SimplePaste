#!/usr/bin/env python

# Ninji's Quick and Dirty Paste Script
# 22nd February 2014

# Licensed under the Do What The Fuck You Want To Public License
# https://github.com/Ninjifox/SimplePaste

import tempfile
import pygments
#Python 2 doesn't like this??
#import pygments.lexers as p_lexers
from pygments.lexers import get_lexer_by_name
import pygments.formatters as p_formatters
import pygments.styles as p_styles
import irc_highlight
import base64
import datetime
import os
import os.path
import sys

OUT_URL = 'http://paste.brokenfox.net'
STYLE = 'monokai'

if len(sys.argv) != 3:
	print('Ninji\'s Quick and Dirty Paste Script')
	print('Usage: %s <language> <path>' % sys.argv[0])
	print('Example: %s python %s' % (sys.argv[0], sys.argv[0]))
	sys.exit()

LANG = sys.argv[1]
IN_FILE = sys.argv[2]

configuration = {
		'in_lang': LANG,
		'linenos': 'table',
		}

def generate_token():
	now = datetime.datetime.now()
	stamp = now.strftime('%y%m%d.%H%M%S.')
	key = base64.b32encode(open('/dev/urandom', 'rb').read(5)).decode('latin-1').lower()
	return stamp+key

def upload(data, destpath):
	if os.path.exists('/home/treeki/bfpaste'):
		with open('/home/treeki/bfpaste/%s' % destpath, 'wb') as f:
			f.write(data)
	else:
		with tempfile.NamedTemporaryFile() as f:
			f.write(data)
			f.flush()
			os.system('chmod a+r %s' % f.name)
			os.system('scp %s otaga:bfpaste/%s' % (f.name, destpath))

def format_text(config, text):
	if config['in_lang'] == 'irc':
		return irc_highlight.highlight(text)
	else:
		lexer = get_lexer_by_name(config['in_lang'])
		style = p_styles.get_style_by_name(STYLE)

		formatter = p_formatters.HtmlFormatter(linenos=config['linenos'], cssclass='pb', style=style)

		html = pygments.highlight(text, lexer, formatter)

		return html


data = open(IN_FILE, 'rb').read().decode('utf-8')
result = format_text(configuration, data)

output = u'''<!DOCTYPE html><html><head>
<!--
	Configuration:
	{config}
	-->
<link rel='stylesheet' href='res/style.css' type='text/css'>
</head><body>
{text}
</body></html>'''.format(
		config=repr(configuration),
		text=result)

token = generate_token()
upload(output.encode('utf-8'), token)
upload(data.encode('utf-8'), 'raw/%s' % token)
print('%s/%s' % (OUT_URL, token))

