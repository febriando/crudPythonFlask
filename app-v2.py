
# coding=utf-8
import sys
import os, shutil
import glob
import re
import numpy as np
import cv2

# Flask utils
from flask import Flask,flash, request, render_template,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os.path
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from datetime import date
from flask_bootstrap import Bootstrap

from sqlalchemy.sql import text
from werkzeug.utils import secure_filename

# Define a flask app
app = Flask(__name__, static_url_path='')
app.secret_key = os.urandom(24)

app.config['HSI_FOLDER'] = 'hsi_images'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy()
db_name = 'memet.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'

# initialize the app with Flask-SQLAlchemy
db.init_app(app)

bootstrap = Bootstrap(app)

@app.route('/uploads/<filename>')
def upload_img(filename):
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/hsi_images/<filename>')
def hsi_img(filename):
    
    return send_from_directory(app.config['HSI_FOLDER'], filename)

class Cust(db.Model):
    __tablename__ = 'cust'
    idcust = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String)
    usia = db.Column(db.Integer)
    incomekecil = db.Column(db.Integer)
    incomebesar = db.Column(db.Integer)
    sex = db.Column(db.String)
    premi = db.Column(db.Integer)
    bklaim = db.Column(db.Integer)
    tklaim = db.Column(db.Integer)
    cakupan = db.Column(db.String)
    produk = db.Column(db.String)
    
    def __init__(self, nama, usia, incomekecil, incomebesar, sex, premi, bklaim, tklaim, cakupan, produk):
        self.nama = nama
        self.usia = usia
        self.incomekecil = incomekecil
        self.incomebesar = incomebesar
        self.sex = sex
        self.premi = premi
        self.bklaim = bklaim
        self.tklaim = tklaim
        self.cakupan = cakupan
        self.produk = produk
        
class AddRecord(FlaskForm):
    # id used only by update/edit
    idcust = HiddenField()
    nama = StringField('Cust name', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid cust name"),
        Length(min=3, max=25, message="Invalid sock name length")
        ])
    usia = IntegerField('Usia', [ InputRequired(),
        NumberRange(min=1, max=999, message="Invalid range")
        ])
    incomekecil = IntegerField('Income terkecil', [ InputRequired(),
        NumberRange(min=1, max=999, message="Invalid range")
        ])
    incomebesar = IntegerField('Income terbesar', [ InputRequired(),
        NumberRange(min=1, max=999, message="Invalid range")
        ])
    sex = SelectField('Jenis kelamin', [ InputRequired()],
        choices=[ ('', ''), ('perempuan', 'Perempuan'),
        ('laki-laki', 'Laki-laki'),])
    premi = IntegerField('Premi per bulan', [ InputRequired(),
        NumberRange(min=1, max=999, message="Invalid range")
        ])
    bklaim = IntegerField('Batas maksimum klaim', [ InputRequired(),
        NumberRange(min=1, max=999, message="Invalid range")
        ])
    tklaim = StringField('Masa tunggu klaim', [ InputRequired(),
        Regexp(r'^[A-Za-z0-9\s\-\']+$', message="Invalid Masa tunggu klaim"),
        Length(min=3, max=25, message="Invalid Masa tunggu klaim name length")
        ])
    cakupan = StringField('Cakupan perlindungan', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Cakupan perlindunga"),
        Length(min=3, max=25, message="Invalid Cakupan perlindunga name length")
        ])
    produk = StringField('Nama produk', [ InputRequired(),
        Regexp(r'^[A-Za-z0-9\s\-\']+$', message="Invalid Nama produk"),
        Length(min=3, max=25, message="Invalid Nama produk length")
        ])
    # updated - date - handled in the route function
    updated = HiddenField()
    submit = SubmitField('Add/Update Record')

@app.route('/', methods=['GET'])
def index():
    # Main page
    # socks = db.session.execute(db.select(Cust).filter_by(style=style).order_by(Cust.name)).scalars()
    cust = db.session.execute(db.select(Cust).order_by(Cust.idcust)).scalars()
    
    return render_template('index.html', cust=cust)
    # check data
    # try:
    #     db.session.query(text('1')).from_statement(text('SELECT 0')).all()
    #     return '<h1>It works.</h1>'
    # except Exception as e:
    #     # e holds description of the error
    #     error_text = "<p>The error:<br>" + str(e) + "</p>"
    #     hed = '<h1>Something is broken.</h1>'
    #     return hed + error_text
    
# add a new cust to the database
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    form1 = AddRecord()
    if form1.validate_on_submit():
        nama = request.form['nama']
        usia = request.form['usia']
        incomekecil = request.form['incomekecil']
        incomebesar = request.form['incomebesar']
        sex = request.form['sex']
        premi = request.form['premi']
        bklaim = request.form['bklaim']
        tklaim = request.form['tklaim']
        cakupan = request.form['cakupan']
        produk = request.form['produk']
        # the data to be inserted into Sock model - the table, socks
        record = Cust(nama, usia, incomekecil, incomebesar, sex, premi, bklaim, tklaim, cakupan, produk)
        # Flask-SQLAlchemy magic adds record to database
        db.session.add(record)
        db.session.commit()
        # create a message to send to the template
        message = f"The data for sock {nama} has been submitted."
        return render_template('add_record.html', message=message)
    else:
    # show validaton errors
    # see https://pythonprogramming.net/flash-flask-tutorial/
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('add_record.html', form1=form1)

if __name__ == '__main__':
        app.run(debug=True)

