
from __future__ import absolute_import
import os
import redis
import cv2
import face_recognition
from werkzeug.utils import secure_filename
from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, TextField, validators


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
redis_url = 'redis://35.231.252.177'
redis_url_edge1 = 'redis://35.231.252.177'
redis_url_edge2 = 'redis://104.199.126.232'
redis_url_edge3 = 'redis://35.224.17.11'

UPLOAD_FOLDER = '/Users/niveditha/Desktop/Images_Surveillance'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    criminalId = TextField('Criminal Id:', validators=[validators.required()])
    pincode = TextField('Pincode:', validators=[validators.required()])


@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        criminalId = request.form['criminalId']
        pincode = request.form['pincode']
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        filepath = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        if form.validate():
            img = cv2.imread(filepath)
            ecd = face_recognition.face_encodings(img)[0]
            key = "c_" + str(ecd)
            pincode = int(pincode)
            if(pincode == 1):
                r = redis.StrictRedis.from_url(redis_url_edge1)
            elif(pincode == 2):
                r = redis.StrictRedis.from_url(redis_url_edge2)
            else:
                r = redis.StrictRedis.from_url(redis_url_edge3)
            r.set(key, name)
            flash('Criminal Record Added!' + name)
        else:
            flash('Error: All the form fields are required. ')

    return render_template('hello.html', form=form)


if __name__ == "__main__":
    app.run()
