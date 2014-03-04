IRC_COLOURS = (
'ffffff', '000000', '00007f', '000093',
'ff0000', '7f0000', '9c009c', 'fc7f00',
'ffff00', '00fc00', '009393', '00ffff',
'0000fc', 'ff00ff', '7f7f7f', 'd2d2d2')

irc_cols = []
for i,col in enumerate(IRC_COLOURS):
	irc_cols.append('.irc%d { color: #%s; }' % (i,col))
	irc_cols.append('.ircbg%d { background-color: #%s; }' % (i,col))


import pygments.formatters as p_formatters
import pygments.styles as p_styles

STYLE = 'monokai'

style = p_styles.get_style_by_name(STYLE)
formatter = p_formatters.HtmlFormatter(cssclass='pb', style=style)
pygments_css = formatter.get_style_defs()

full_css = '''
body {{ background: #000; line-height: 110%; }}
.irclog, pre {{
	padding: 0.5em;
	font-family: "Consolas", "DejaVu Sans Mono", monospace;
	font-size: 12px;
}}
pre {{
	white-space: pre-wrap;
}}
.lineno {{ color: #999; padding-right: 10px; }}
.linenodiv {{ color: #bbb; padding-right: 8px; }}

{pygments_css}

.i_s, .i_a, .i_m {{
	margin: 4px;
}}
div>span:first-child {{ color: #999; }}
/*div>span:first-child:before {{ content: '['; }}
div>span:first-child:after {{ content: ']'; }}*/
.i_n {{ font-weight: bold; }}
.i_s>.i_n:before {{ content: '<'; }}
.i_s>.i_n:after {{ content: '>'; }}
.i_a {{ color: #ae81ff; }}
.i_m {{ color: #9c977c; }}

{irc_cols}
'''.format(
		irc_cols='\n'.join(irc_cols),
		pygments_css=pygments_css
		)

print(full_css)

