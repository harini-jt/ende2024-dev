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

@app.route('/')
def home():
    return render_template('home.html')



@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

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


# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     message = ''
#     # check if user is logged in
#     if "email" in session:
#         return redirect(url_for("profile"))
#     # if method is post
#     if request.method == "POST":
#         username = request.form.get("name")
#         email = request.form.get("email")
#         password1 = request.form.get("password1")
#         password2 = request.form.get("password2")
#         role = '1'

#         user_found = users.find_one({"email": email})
#         if user_found:
#             message = 'This email is already registered to an account'
#             return render_template('signup.html', signupmessage=message)
#         if password1 != password2:
#             message = 'Passwords should match!'
#             return render_template('signup.html', signupmessage=message)
#         else:
#             # hash the password and encode it
#             hashed = password2
#             # assigning them in a dictionary
#             user_input = {
#                 'name': username,
#                 'email': email,
#                 'password': hashed,
#                 'role': role,
#                 'isOnline': True,
#                 'update': False
#             }
#             # insert the dictionary in the database
#             users.insert_one(user_input)
#             # find the new user and assign it to session
#             user_data = users.find_one({"email": email})
#             session['email'] = user_data['email']
#             # if registration is successful, redirect to profile page
#             return redirect(url_for('profile'))
#     return render_template('signup.html', signupmessager=message)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    message = ''
    # check if user is logged in
    if "email" in session:
        return redirect(url_for("profile"))
    # if method is post
    if request.method == "POST":
        username = request.form.get("name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        role = '1'

        user_found = users.find_one({"email": email})
        if user_found:
            message = 'This email is already registered to an account'
            return render_template('signup.html', signupmessage=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('signup.html', signupmessage=message)
        else:
            # hash the password and encode it
            hashed =password2
            # assigning them in a dictionary
            user_input = {
                'name': username,
                'email': email,
                'password': hashed,
                'mobile': '',
                'country': '',
                'altemail': '',
                'affiliation': '',
                'role': role,
                'isOnline': True,
                'updated': False
            }
            # insert the dictionary in the database
            users.insert_one(user_input)
            # find the new user and assign it to session
            user_data = users.find_one({"email": email})
            session['email'] = user_data['email']
            session['loggedin'] = True
            # if registration is successful, redirect to profile page
            return redirect(url_for('profile'))
    return render_template('signup.html', signupmessager=message)

@app.route('/profile', methods=['GET', 'POST'])
def profile(): 
    if "email" in session:
        email = session["email"]
        user = users.find_one({"email": email})
        message = {
            'email': user['email'],
            'name': user['name'],
            'mobile': user['mobile'],
            'country': user['country'],
            'altemail': user['altemail'],
            'affiliation': user['affiliation']
        }
        if request.method == "POST":
            message['name'] = request.form['name']
            message['mobile'] = request.form['mobile']
            message['country'] = request.form['country']
            message['altemail'] = request.form['altemail'] if 'altemail' in request.form else ''
            message['affiliation'] = request.form['affiliation'] if 'affiliation' in request.form else ''
            # mongo db
            users.update_one(user, {'$set': {'name': message['name'],
                'mobile': message['mobile'],
                'country': message['country'],
                'altemail': message['altemail'],
                'affiliation': message['affiliation'],
                'updated': True
                }
            })
        return render_template('profile.html',  message=message)
    else:
        return redirect(url_for("login"))


@app.route('/schedule', methods=['GET'])
def schedule():
    return render_template('schedule.html')

# logout route
@app.route('/logout', methods=["POST", "GET"])
def logout():
    if "email" in session:
        db.users.find_one_and_update(
            {'email': session['email']},
            {'$set': {'isOnline': False}})
        session.pop("email", None)
        session.pop('loggedin', None)
        return redirect('/')
    else:
        return render_template('signup.html')
