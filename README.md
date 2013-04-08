MWPDFUpload 1) helps you create PNG images out of PDF and 2) post those images off to a MediaWiki site.

What you need
-------------
* [MuPDF](http://www.mupdf.com/) - download the source and run `make`
* All the things in the `requirements.txt` file

How you use it
--------------
* Create a configuration file called `config.py` in the same directory as this code, here's an example:
    #!/usr/bin/env python
    
    # Configuration file for mw-pdf-upload
    import os
    from os.path import expanduser
    HOME = expanduser("~")
    
    URL="http://xxxxx.com/w/api.php"
    USER="xxx"
    PASS="xxxxxxx"
    MUPDF=HOME+"/mupdf-1.2-source/build/debug/mudraw"

* Prep your input file, see (`example_input.txt` for an example). Each line consists of the name of the file you want 
  to upload (relative to the current directory), followed by a space, and then all the categories you want to put that
  document under. 
* Run `cat input.txt | python main.py` to start the upload. 

What it should do
-----------------
You'll end up with page of the PDF on the MediaWiki site having some kind of permutation of the filename provided, with a summary page linking them all together. 
