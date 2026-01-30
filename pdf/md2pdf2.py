# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from markdown import markdown
from weasyprint import HTML, CSS

def md2pdf2(pdf_file_path, md_content=None,
					stylesheets=None):

	# Convert markdown to html
	raw_html = markdown(md_content, extensions=['tables', 'footnotes'])

	# Weasyprint HTML object
	html = HTML(string=raw_html, encoding='utf-8')

	# Get styles
	for p in stylesheets:
		# Generate PDF
		html.write_pdf(p + pdf_file_path, stylesheets=[CSS(string=stylesheets[p])])

	return
