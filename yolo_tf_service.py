import os
import time
import string
import random
import io
import cv2
import numpy as np
import jsonpickle

from flask import Flask, flash, request, redirect, url_for, Response
from flask import send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from YOLO_small_tf import YOLO_TF

# curl -X POST -F 'file=@client/images/person1.jpg' http://localhost:5000/process

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def home():
    return redirect(url_for('process_image'))


@app.route('/process', methods=['GET', 'POST'])
def process_image():
    if request.method == 'POST':

        if len(request.files.keys()) == 0:
            nparr = np.fromstring(request.data, np.uint8)
            img_mat = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return process(img_mat)

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            in_memory_file = io.BytesIO()
            file.save(in_memory_file)
            nparr = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
            img_mat = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return process(img_mat, file.filename)

    return '''
    <!doctype html>
    <title>Process new image</title>
    <h1>Process new image</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Process>
    </form>
    '''


def process(img_mat, filename=None):
    results, elapsed_seconds = yolo.detect_from_cvmat(img_mat)

    if filename:
        response = {'filename': filename,
                    'results': results, 'elapsed seconds': elapsed_seconds}
    else:
        response = {'results': results, 'elapsed seconds': elapsed_seconds}

    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    yolo = YOLO_TF()
    app.run(host='0.0.0.0')
