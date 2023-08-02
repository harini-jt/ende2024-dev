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
    # check if user is logged in
    if "email" in session:
        return redirect(url_for("profile"))
    # if method is post
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # find the user with the email
        user_found = users.find_one({"email": email})
        # if user is found
        if user_found and (not user_found['role'] == 0):
            # check if password matches
            if password == user_found['password']:
                # assign the user to session
                session['email'] = user_found['email']
                # redirect to profile page
                return redirect(url_for("profile"))
            else:
                message = 'Wrong Credentials'
                return render_template('login.html', signupmessage=message)
         # ADMIN
        elif user_found and user_found['role'] == os.environ.get('ADMIN'):
            email_val = user_found['email']
            passwordcheck = user_found['password']
            # encode the password and check if it matches
            if password == passwordcheck:
                session["email"] = email_val
                users.find_one_and_update({'email': session['email']}, {
                    '$set': {'isOnline': True}})
                return redirect(url_for("admin"))

            else:
                if "email" in session:
                    users.find_one_and_update({'email': session['email']}, {
                        '$set': {'isOnline': True}})
                    return redirect(url_for("admin"))
                message = 'Wrong password'
                return render_template('login.html', message=message)

        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)
