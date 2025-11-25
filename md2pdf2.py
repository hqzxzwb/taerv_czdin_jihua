# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from markdown2 import markdown, markdown_path
from weasyprint import HTML, CSS

def md2pdf2(pdf_file_path, md_content=None,
					css_file_paths=None, base_url=None):

	# Convert markdown to html
	raw_html = ''
	extras = ['cuddled-lists', 'tables', 'footnotes']
	raw_html = markdown(md_content, extras=extras)

	# Weasyprint HTML object
	html = HTML(string=raw_html, base_url=base_url)

	# Get styles
	for p in css_file_paths:
		# Generate PDF
		html.write_pdf(p[0] + pdf_file_path, stylesheets=[CSS(filename=p)])

	return
