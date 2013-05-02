#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import shutil
import shlex
import subprocess
import sys
import tempfile

from subprocess import PIPE
from wikitools import Wiki, File, Page 
from config import *

def sortpng(filename):
	numeric, dot, extension = filename.partition('.')
	return int(numeric)

def _get_fname_cat_tuple_quoted(line):
	items = shlex.split(line)
	return items[0], ' '.join(items[1:])

def _get_fname_cat_tuple(line):
	fname, junk, categories = line.partition(" ")
	return fname, categories

def get_fname_cat_tuple(line):
	if "\"" in line:
		return _get_fname_cat_tuple_quoted(line)
	return _get_fname_cat_tuple(line)

# Upload the images under a [[Category:MWPDFUpload]] [user_categories] tag
# Create a summary page with the page_name [[user_categories:1]]
# In practice: the FIRST category provided will be used to create the summary
def main():

	# Connect to the site 
	logging.info("Connecting to site: '%s'", URL)
	wiki = Wiki(URL)
	logging.info("Logging in...")
	if not wiki.login(USER, PASS):
		logging.critical("Authentication failed, check your details!")
		sys.exit(1)

	# Temporary datastructures
	pending_upload = []
	pending_summary = []
	warnings = []
	no_delete = set([])

	for line in sys.stdin:
		# Read in the filename and categories
		fname, categories = get_fname_cat_tuple(line)
		categories = map(lambda x: "[[Category:%s]]" % x, categories.strip().split(" "))
		categories.append("[[Category:MWPDFUploads]]")

		# Check the file is there
		if not os.path.exists(fname):
			logging.critical("Can't find file: %s", fname)
			sys.exit(1)
		if fname[-4:] != ".pdf":
			logging.critical("Can't interpret that file format: %s", fname)
			sys.exit(1)

		# Create a temporary directory 
		tmp_path = tempfile.mkdtemp()
		pending_upload.append((fname, categories, tmp_path))

	try:
		for fname, categories, tmp_path in pending_upload:
			pending_summary = []
			logging.info("=========================")
			logging.info("Filename: %s", fname)
			logging.info("Categories:%s",categories)
			
			logging.info("\nConverting...")
			args = ["-o%s/%%d.png" % (tmp_path), os.path.join(os.getcwd(),fname)]
			logging.debug("Calling '%s' with args '%s'", MUPDF, args)
			subprocess.check_call([MUPDF]+args)
			logging.info("\nUploading...")

			last_png_fname = None
			for png_fname in sorted(os.listdir(tmp_path), key = sortpng):
				last_png_fname = png_fname

			for png_fname in sorted(os.listdir(tmp_path), key = sortpng):
				counter = sortpng(png_fname)
				logging.info("\tUploading %s...", png_fname)
				file_description = "\n".join(categories) + "\n[[Category:MWPDFUpload]]"
				fp_path = os.path.join(tmp_path, png_fname)
				fp_obj = open(os.path.join(tmp_path, png_fname), 'r')
				file_root = re.sub("[^a-zA-Z0-9]","-",fname) 
				file_name = file_root + str(counter) + ".png"

				# Create the Wikimedia file entry 
				wiki_file = File(wiki, file_name, True, True)
				if "--skipfile" not in sys.argv:
					wiki_file.upload(fp_obj)
				if not wiki_file.exists:
					logging.error("Wiki file '%s' doesn't exist!",wiki_file.title)
					warnings.append((os.path.join(tmp_path, png_fname), wiki_file.title))
					no_delete.add(tmp_path)
					
				logging.info("\tUploaded as %s",wiki_file.title)
			
				# Create a node page 
				node_page = Page(wiki, file_name)
				node_content = "<center><table class=\"wikitable\"><tr>"
				if counter > 1:
					node_content += "<td>[[%s |« Previous page]] </td>"  % (file_root + str((counter-1)) + ".png",)
				else:
					node_content += "<td>'''(First page)'''</td>"
				if png_fname == last_png_fname:
					node_content += "<td>'''(Last page)'''</td>"
				else:
					node_content += "<td>[[%s |Next page »]]" % (file_root + str((counter+1)) + ".png", ) + "</td>"

				node_content += "</tr>\n<tr><td colspan=\"2\">"
				node_content +=  "[[%s|500px]]" % (wiki_file.title)
				node_content += "</tr></table></center>\n\n"

				# Extract the page's content from the PDF
				extract = "pdf2txt -p %d -t text \"%s\"" % (counter, fname)
				logging.debug("Extracting with args: %s",extract)
				p = subprocess.Popen(extract, shell=True, stdout=PIPE)
				p_stdout, p_stderr = p.communicate()
				logging.error(p_stderr)
				node_content += p_stdout.decode("utf-8").encode("ascii","xmlcharrefreplace") + "\n"
				node_content += "\n".join(categories)
				print node_content
				node_page.edit(text=node_content, summary = "Automatic node page by MWPDFUpload", skipmd5=True, bot=True)
			
				pending_summary.append(wiki_file.title)


	finally:
		logging.info("=========================")
		logging.info("Cleaning up...")
		for fname, categories, tmp_path in pending_upload:
			if tmp_path not in no_delete:
				logging.info("Deleting temp directory '%s'...", tmp_path)
				shutil.rmtree(tmp_path)

		logging.info("Logging out...")
		wiki.logout()
		if len(warnings) > 0:
			print >> sys.stderr, "The following files didn't upload:"
			for fname, title in warnings:
				print >> sys.stderr, "\t", fname, title


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	main()
