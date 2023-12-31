import os
import pymongo
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
from bson.binary import Binary

# set app as a Flask instance
app = Flask(__name__)
# set the secret key
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = './static/uploads'
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
# login route
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

# signup route
@app.route('/signup', methods = ['GET', 'POST'])
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

# profile route
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

# upload route
@app.route('/upload_abstract', methods=['GET', 'POST'])
def upload_abstract():
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        # check if the post request has the file part
        if "email" in session:
            if 'file' not in request.files:
                return redirect(request.url)
            
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                #  find user
                email = session["email"]
                user = users.find_one({"email": email})
                #  get user name
                user_name = user['name']
                # save file in user document
                with open(app.config['UPLOAD_FOLDER'] + '\\'+ filename, "rb") as f:
                    encoded = Binary(f.read())
                    # user.insert({"filename": filename, "file": encoded, "description": "test" })
                    # user.update({"filename": filename, "file": encoded, "description": "test" })
                    # save user in db
                    users.update_one(user, {
                        "$set": {
                            "abstracts":{
                                "filename": filename,
                                "file": encoded, 
                                "description": "test"
                            }
                        }})
                    # users.insert({"filename": filename, "file": encoded, "description": "test" })
                    print('file saved in db')
                #  save file in folder
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template('upload_abstract.html', message="File uploaded successfully 😄")
            elif not allowed_file(file.filename):
                return render_template('upload_abstract.html', message="Check the file extension 😞")
        else:
            return render_template("/login.html")
    return render_template('upload_abstract.html', message='Upload your abstract here')



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