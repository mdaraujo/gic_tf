import os
import time
import string
import random

from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from YOLO_small_tf import YOLO_TF

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def home():
    return redirect(url_for('process_file'))


@app.route('/process', methods=['GET', 'POST'])
def process_file():
    if request.method == 'POST':
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
            filename = secure_filename(file.filename)
            ts = time.time()
            filename = str(ts).replace('.', '_') + '_' + \
                id_generator() + '_' + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return process(filename)

    return '''
    <!doctype html>
    <title>Process new image</title>
    <h1>Process new image</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Process>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/process/<filename>')
def process(filename):
    results = yolo.detect_from_file(UPLOAD_FOLDER + '/' + filename)

    template = '''
    <!doctype html>
    <h2>Filename: {{ filename }}</h2>
    <h3>Results: {{ results }}</h3>
    '''

    return render_template_string(template, filename=filename, results=results)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


if __name__ == '__main__':
    yolo = YOLO_TF()
    app.run(host='0.0.0.0')


# TO TEST:
# curl -X POST -F 'file=@test_images/person1.jpg' http://localhost:5000/process
