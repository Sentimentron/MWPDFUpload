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
You'll end up with page of the PDF on the MediaWiki site having some kind of permutation of the filename provided, 
with a summary page linking them all together. 

License
-------
Copyright (c) 2013 Richard Townsend
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.
