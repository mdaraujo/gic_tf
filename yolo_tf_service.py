import os
import time
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from YOLO_small_tf import YOLO_TF

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

global yolo


@app.route('/')
def home():
    return redirect(url_for('upload_file'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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
            filename = str(ts) + "_" + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('process',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
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


if __name__ == '__main__':
    yolo = YOLO_TF()
    app.run(host='0.0.0.0')


# TODO curl not working - sending POST on redirect
# curl -L -X POST -F 'file=@test_images/person.jpg' http://localhost:5000/upload
