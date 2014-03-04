import re

# This bit was casually stolen from Pygments's HTMLFormatter
_escape_html_table = {
	ord('&'): u'&amp;',
	ord('<'): u'&lt;',
	ord('>'): u'&gt;',
	ord('"'): u'&quot;',
	ord("'"): u'&#39;',
}

# MY STUFF

def match_colour_string(s, pos):
	if pos < len(s):
		first = ord(s[pos])
		if first >= 0x30 and first <= 0x39:
			first -= 0x30
			if (pos + 1) < len(s):
				second = ord(s[pos + 1])
				if second >= 0x30 and second <= 0x39:
					second -= 0x30
					attempt = (first * 10) + second
					if attempt < 0 or attempt > 15:
						return (pos, None)
					else:
						return (pos + 2, attempt)
			return (pos + 1, first)
	return (pos, None)

def match_colour_pair(s, pos):
	fg = None
	bg = None
	pos, fg = match_colour_string(s, pos)

	if fg != None:
		if pos < len(s):
			if s[pos] == ',':
				pos, bg = match_colour_string(s, pos + 1)

	return pos, fg, bg

def add_tokens(tokens, line):
	flag_b = False
	flag_i = False
	flag_u = False
	flag_c = False
	fg = None
	bg = None

	runpos = -1
	pos = 0
	strlen = len(line)

	while pos < strlen:
		c = ord(line[pos])
		if c < 0x20:
			if runpos != -1:
				tokens.append(line[runpos:pos].translate(_escape_html_table))
				runpos = -1

			if c == 2:
				flag_b = not flag_b
				if flag_b:
					tokens.append('<b>')
				else:
					tokens.append('</b>')
			elif c == 0x1D:
				flag_i = not flag_i
				if flag_i:
					tokens.append('<i>')
				else:
					tokens.append('</i>')
			elif c == 0x1F:
				flag_u = not flag_u
				if flag_u:
					tokens.append('<u>')
				else:
					tokens.append('</u>')
			elif c == 0xF:
				if flag_b:
					tokens.append('</b>')
					flag_b = False
				if flag_i:
					tokens.append('</i>')
					flag_i = False
				if flag_u:
					tokens.append('</u>')
					flag_u = False
				if flag_c:
					tokens.append('</span>')
					flag_c = False
			elif c == 3:
				if flag_c:
					tokens.append('</span>')
					flag_c = False
				pos, wfg, wbg = match_colour_pair(line, pos + 1)

				if wfg == None:
					fg = None
					bg = None
				else:
					fg = wfg
					if wbg != None:
						bg = wbg

				if wfg != None or wbg != None:
					cls = []
					if wfg != None:
						cls.append('irc%d' % wfg)
					if wbg != None:
						cls.append('ircbg%d' % wbg)
					tokens.append('<span class=\'%s\'>' % ' '.join(cls))
					flag_c = True
				continue
		else:
			if runpos == -1:
				runpos = pos
		pos += 1

	if runpos != -1:
		tokens.append(line[runpos:pos].translate(_escape_html_table))

	if flag_b:
		tokens.append('</b>')
	if flag_i:
		tokens.append('</i>')
	if flag_u:
		tokens.append('</u>')
	if flag_c:
		tokens.append('</span>')

def nick_hash(nick):
	h = 0
	for c in nick:
		h = (((h * 17) + ord(c)) & 0xFFFFFFFF)
	return h

def hsl_value(n1, n2, hue):
	if hue > 6.0:
		hue -= 6.0
	elif hue < 0.0:
		hue += 6.0
	
	if hue < 1.0:
		return n1 + (n2 - n1) * hue
	elif hue < 3.0:
		return n2
	elif hue < 4.0:
		return n1 + (n2 - n1) * (4.0 - hue)
	else:
		return n1

def calc_hsl(h, s, l):
	if s == 0:
		v = int(l*255.0)
		return (v,v,v)
	else:
		if l <= 0.5:
			m2 = l * (1.0 + s)
		else:
			m2 = l + s - l * s
		m1 = 2.0 * s - m2

		r = int(hsl_value(m1, m2, h * 6.0 + 2.0) * 255.0)
		g = int(hsl_value(m1, m2, h * 6.0) * 255.0)
		b = int(hsl_value(m1, m2, h * 6.0 - 2.0) * 255.0)

		return (r,g,b)

def calc_colour(nick):
	h = nick_hash(nick)

	hue = (h & 0xFF0000) >> 16
	sat = (h & 0xFF00) >> 8
	lum = h & 0xFF

	return calc_hsl(hue / 255.0, 0.5 + (sat / 765.0), 0.4 + (lum / 1020.0))


def add_timestamp(tokens, ts):
	tokens.append('<span>%s</span>' % ts)
def add_nick(tokens, nick):
	r,g,b = calc_colour(nick)
	tokens.append('<span class=\'i_n\' style=\'color:#%02x%02x%02x\'>%s</span>' % (r,g,b, nick))

_re_head = r'^([^[]*\[..:..:..\]) '
_speech_regex = re.compile(_re_head + r'<([^>]+)> (.+)$')
_notice_regex = re.compile(_re_head + r'\*\*\* (.+)$')
_action_regex = re.compile(_re_head + r'\* ([^ ]+) (.+)$')

def proc_line(tokens, line):
	m = _speech_regex.match(line)
	if m:
		tokens.append('<div class=\'i_s\'>')
		ts, nick, text = m.groups()
		add_timestamp(tokens, ts)
		tokens.append(' ')
		add_nick(tokens, nick)
		tokens.append(' ')
		add_tokens(tokens, text)
		tokens.append('</div>')
		return

	m = _notice_regex.match(line)
	if m:
		tokens.append('<div class=\'i_m\'>')
		ts, text = m.groups()
		add_timestamp(tokens, ts)
		tokens.append(' *** ')
		add_tokens(tokens, text)
		tokens.append('</div>')
		return

	m = _action_regex.match(line)
	if m:
		tokens.append('<div class=\'i_a\'>')
		ts, nick, text = m.groups()
		add_timestamp(tokens, ts)
		tokens.append(' * ')
		add_nick(tokens, nick)
		tokens.append(' ')
		add_tokens(tokens, text)
		tokens.append('</div>')
		return

	if line == '--':
		tokens.append('<div class=\'i_a\'>----</div>')
		return

	stripped_line = line.strip()
	if len(stripped_line) > 0:
		print('Warning: We didn\'t parse this? : [%s]' % line)

def highlight(text):
	lines = text.split('\n')
	tokens = ['<div class=\'pb irclog\'>']

	for line in lines:
		proc_line(tokens, line)
		tokens.append('\n')

	tokens.append('</div>')
	return u''.join(tokens)

