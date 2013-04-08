#!/usr/bin/env python

import logging
import os
import shutil
import suprocess
import sys
import tempfile

from wikitools import Wiki, File 
from config import *

# Upload the images under a [[Category:MWPDFUpload]] [user_categories] tag
# Create a summary page with the page_name [[user_categories:1]]
# In practice: the FIRST category provided will be used to create the summary
def main():

	# Connect to the site 
	logging.debug("Connecting to site: '%s'", URL)
	wiki = Wiki(URL)
	logging.debug("Logging in...")
	if not wiki.login(USER, PASS):
		logging.critical("Authentication failed, check your details!")
		sys.exit(1)

	# Temporary datastructures
	pending_upload = []
	pending_summary = []

	for line in sys.stdin:
		# Read in the filename and categories
		fname, junk, categories = line.partition("\t")
		categories = map(lambda x: "[[Category:%s]]" % x, categories.split(" "))

		# Check the file is there
		if not os.path.exists(fname):
			logging.critical("Can't file file: %s", fname)
			sys.exit(1)
		if fname[-4:] != ".pdf":
			logging.critical("Can't interpret that file format: %s", fname)
			sys.exit(1)

		# Create a temporary directory 
		tmp_path = tempfile.mkdtemp()
		pending_upload.append((fname, categories, tmp_path))

	try:
		for fname, categories, tmp_path in pending_upload:
			logging.info("=========================")
			logging.info("Filename: %s", fname)
			logging.info("Categories:%s",categories)
			
			logging.info("\nConverting...")
			args = ["-o %s/%%d.png" % (tmp_path), fname]
			logging.debug("Calling '%s' with args '%s'", MUPDF, args)
			subprocess.check_call([MUPDF]+args)
			logging.info("\nUploading...")

			for png_fname in os.listdir(tmp_path):
				logging.info("\tUploading %s...", png_fname)
				file_description = "\n".join(categories) + "\n[[Category:MWPDFUpload]]"
				file_name = fname + png_fname

				fp_obj = open(png_fname, 'r')

				# Create the Wikimedia file entry 
				wiki_file = File(wiki, file_name)
				wiki_file.upload(fp_obj)
				if not wiki_file.exists:
					raise Exception("For some reason, the file doesn't exist!")

				pending_summary.append(wiki_file.title)

		logging.info("=========================")
		logging.info("Generating summary page...")

		page_template = "[[File:%s|thumb|center]]"
		page_content = '\n'.join(page_template % (i,) for i in pending_summary)
		page = Page(wiki, fname)
		page.edit(text=page_content, summary="Automatic summary by MWPDFUpload", bot=True, watch=True)
		if not page.exists:
			raise Exception("For some reason, creating the summary page failed.")

	finally:
		logging.info("=========================")
		logging.info("Cleaning up...")
		for fname, categories, tmp_path in pending_upload:
			logging.info("Deleting temp directory '%s'...", tmp_path)
			shutil.rmtree(tmp_path)

		logging.info("Logging out...")
		wiki.logout()


if __name__ == "__main__":
	logging.basicConfig(loglevel=DEBUG)
	main()