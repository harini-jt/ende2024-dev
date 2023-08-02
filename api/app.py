import os
import pymongo
from flask import Flask, jsonify, request, render_template, session, redirect, url_for


# set app as a Flask instance
app = Flask(__name__)
# set the secret key
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ALLOWED_EXTENSIONS = {'pdf'}

client = pymongo.MongoClient(os.environ.get('MONGO_URI'))
db = client.get_database(os.environ.get('DB_NAME'))
users = db[os.environ.get('USERS_COLLECTION')]

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# testing login route
@app.route('/home', methods=['GET'])
def back_home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    message = 'Please login to your account'
    return render_template('login.html', message=message)
