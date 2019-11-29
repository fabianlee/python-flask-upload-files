#!/usr/bin/env python
"""
Flask application that receives uploaded content from browser

"""
import sys
import random
import string
import time
import os
import tempfile
from datetime import datetime
import flask
from werkzeug.utils import secure_filename

# whitelist of file extensions
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = flask.Flask(__name__)

def allowed_file(filename):
    """ whitelists file extensions for security reasons """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def entry_point():
    """ simple entry for test """
    return flask.render_template('index.html')

@app.route('/upload_form')
def upload_form():
    return flask.render_template('upload_form.html')

@app.route("/singleuploadchunked/<filename>", methods=["POST", "PUT"])
def single_upload_chunked(filename=None):
    """Saves single file uploaded from <input type="file">, uses stream to read in by chunks

       When using direct access to flask.request.stream
       you cannot access request.file or request.form first, 
       otherwise stream is already parsed and empty
       This is because of internal workings of werkzeug

       Positive test:
       curl -X POST http://localhost:8080/singleuploadchunked/car.jpg -d "@tests/car.jpg"

       Negative test (no file uploaded, no Content-Length header):
       curl -X POST http://localhost:8080/singleuploadchunked/car.jpg
       Negative test (not whitelisted file extension):
       curl -X POST http://localhost:8080/singleuploadchunked/testdoc.docx -d "@tests/testdoc.docx"
    """
    if not "Content-Length" in flask.request.headers:
        add_flash_message("did not sense Content-Length in headers")
        return flask.redirect(flask.url_for("upload_form"))

    if filename is None or filename=='':
        add_flash_message("did not sense filename in form action")
        return flask.redirect(flask.url_for("upload_form"))

    if not allowed_file(filename):
        add_flash_message("not going to process file with extension " + filename)
        return flask.redirect(flask.url_for("upload_form"))


    print("Total Content-Length: " + flask.request.headers['Content-Length'])
    fileFullPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    chunk_size = app.config['CHUNK_SIZE']
    with open(fileFullPath, "wb") as f:
        reached_end = False
        while not reached_end:
            chunk = flask.request.stream.read(chunk_size)
            if len(chunk) == 0:
                reached_end = True
            else:
                sys.stdout.write(".")
                #print("wrote chunk of {}".format(len(chunk)))
                f.write(chunk)
        print("")
    return flask.redirect(flask.url_for("upload_form"))
    


@app.route("/multipleupload", methods=["GET","POST", "PUT"])
def multiple_upload(file_element_name="files[]"):
    """Saves files uploaded from <input type="file">, can be multiple files
    
       Positive Test (single file):
       curl -X POST http://localhost:8080/multipleupload -F "files[]=@tests/car.jpg"
       Positive Test (multiple files):
       curl -X POST http://localhost:8080/multipleupload -F "files[]=@tests/car.jpg" -F "files[]=@tests/testdoc.pdf"

       Negative Test (using GET method):
       curl -X GET http://localhost:8080/multipleupload
       Negative Test (no input file element):
       curl -X POST http://localhost:8080/multipleupload
       Negative Test (not whitelisted file extension):
       curl -X POST http://localhost:8080/multipleupload -F "files[]=@tests/testdoc.docx"
    """

    # must be POST/PUT
    if not (flask.request.method in ['POST','PUT']):
        add_flash_message("Can only upload on POST/PUT methods")
        return flask.redirect(flask.url_for("upload_form"))

    # must have <input type="file"> element
    if file_element_name not in flask.request.files:
        add_flash_message('No files uploaded')
        return flask.redirect(flask.url_for("upload_form"))

    # get list of files uploaded
    files = flask.request.files.getlist(file_element_name)

    # if user did not select file, filename will be empty
    if len(files)==1 and files[0].filename == '':
        add_flash_message('No selected file')
        return flask.redirect(flask.url_for("upload_form"))

    # loop through uploaded files, saving
    for ufile in files:
        filename = secure_filename(ufile.filename)
        if allowed_file(filename):
            print("uploading file {} of type {}".format(filename,ufile.content_type))
            ufile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flask.flash("Just uploaded: " + filename)
        else:
            add_flash_message("not going to process file with extension " + filename)
    return flask.redirect(flask.url_for("upload_form"))
    
def add_flash_message(msg):
    """Provides message to end user in browser"""
    print(msg)
    flask.flash(msg)

if __name__ == "__main__":
    #print("tempdir: " + tempfile.gettempdir())
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
    app.config['CHUNK_SIZE'] = 4096
    # secret key used for flask.flash of messages
    app.secret_key = 'abc123'

    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
