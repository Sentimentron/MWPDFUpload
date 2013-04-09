#!/usr/bin/env python

import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pyPdf
from wikitools import Wiki, File, Page 
from config import *

def sortpng(filename):
	numeric, dot, extension = filename.partition('.')
	return int(numeric)

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
		fname, junk, categories = line.partition(" ")
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
			pdf_file = pyPdf.PdfFileReader(file(fname, "rb"))

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
				wiki_file.upload(fp_obj)
				if not wiki_file.exists:
					logging.error("Wiki file '%s' doesn't exist!",wiki_file.title)
					warnings.append((os.path.join(tmp_path, png_fname), wiki_file.title))
					no_delete.add(tmp_path)
					
				logging.info("\tUploaded as %s",wiki_file.title)
				
				# Create a node page 
				node_page = Page(wiki, file_name)
				node_content = "<table class=\"wikitable\"><tr><td>"
				if counter > 1:
					node_content += "[[%s |Previous Slide ]] </td>"  % (file_root + str((counter-1)) + ".png",)
				node_content += "<td>[[%s | Next Slide]]</tr></table>" % (file_root + str((counter+1)) + ".png")

				node_content +=  "[[%s|frame|center]]" % (wiki_file.title)
				# Extract the page's content from the PDF
				node_content += " ".join(pdf_file.getPage(counter-1).extractText().strip().split()).encode("ascii","ignore")
				node_content += "\n".join(categories)
				node_page.edit(text=node_content, summary = "Automatic node page by MWPDFUpload")
				
				pending_summary.append(wiki_file.title)

			logging.info("=========================")
			logging.info("Generating summary page...")

			page_template = "[[%s|frame|center]]"
			page_content = '\n'.join(page_template % (i,) for i in pending_summary) + '\n'.join(categories)
			page = Page(wiki, fname)
			page.edit(text=page_content, summary="Automatic summary by MWPDFUpload", bot=True, watch=True)
			if not page.exists:
				raise Exception("For some reason, creating the summary page failed.")

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
