import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from utils.helpers import connect_db, isAdmin
from io import BytesIO
from datetime import datetime
# set app as a Flask instance
app = Flask(__name__)
# set the secret key
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


# users
connection = connect_db()
users = connection['users']
db = connection['db']
courses = db[os.environ.get('COURSES_COLLECTION')]

# home route


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


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
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            # assigning them in a dictionary
            user_input = {
                'name': username,
                'email': email,
                'password': hashed,
                'role': role,
                'isOnline': True
            }
            # insert the dictionary in the database
            users.insert_one(user_input)
            # find the new user and assign it to session
            user_data = users.find_one({"email": email})
            session['email'] = user_data['email']
            # if registration is successful, redirect to profile page
            return redirect(url_for('profile'))
    return render_template('signup.html', signupmessager=message)


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
        if user_found and (not isAdmin(user_found['role'])):
            # check if password matches
            if bcrypt.hashpw(password.encode('utf-8'), user_found['password']) == user_found['password']:
                # assign the user to session
                session['email'] = user_found['email']
                # redirect to profile page
                return redirect(url_for("profile"))
            else:
                message = 'Wrong Credentials'
                flash('wrong Credentials...!')
                return render_template('login.html', signupmessage=message)
         # ADMIN
        elif user_found and user_found['role'] == os.environ.get('ADMIN'):
            email_val = user_found['email']
            passwordcheck = user_found['password']
            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
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

# user profile route


@app.route('/profile', methods=["POST", "GET"])
def profile():
    message={
            'email': '', 
            'name': '',
            'mobile': '',
            'nationality': '',
            'altemail': '',
            'affiliation': ''
        }
    if "email" in session:
        email = session["email"]
        user = users.find_one({"email": email})
        
        if(user['updated'] != True):
            message['email'], message['name'] = user['email'], user['name']
            return render_template('profile.html',  message=message)
        else:
            pass
        # return render_template('profile.html', email=email)
        # if post method
        # if request.method == "POST":
        #     print('post method called')
        #     username = request.form.get("name")
        #     mobile = request.form.get("mobile")
        #     nationality = request.form.get("nationality")
        #     altemail = request.form.get("altemail")
        #     affiliation = request.form.get("affiliation")
        #     # # print the values
        #     print(username, mobile, nationality, altemail, affiliation) 
        #     # # update user details
        #     users.update(user, {
        #         '$set': {
        #             'name': username,
        #             'mobile': mobile,
        #             'nationality': nationality,
        #             'altemail': altemail,
        #             'affiliation': affiliation,
        #             'updated': True
        #         }
        #     })
        #     print('user updated')
            # if user['updated'] == True:
            #     message={
            #         'email': user['email'], 
            #         'name': user['name'],
            #         'mobile': user['mobile'],
            #         'nationality': user['nationality'],
            #         'altemail': user['altemail'] if user['altemail'] else '',
            #         'affiliation': user['affiliation'] if user['affiliation'] else '',
            #     }
            #     print(message)
    else: 
        return redirect(url_for("login"))
    return render_template('profile.html', message = message)



    message={
            'email': '',
            'name': '',
            'mobile': '',
            'nationality': '',
    }
    if "email" in session:
        email = session["email"]
        user = users.find_one({"email": email})
        message['email'], message['name'] = user['email'], user['name']
        # 
        if request.method == "POST":
            print('post method called')
            username = request.form.get("name")
            mobile = request.form.get("mobile")
            nationality = request.form.get("nationality")
            # # print the values
            print(username, mobile, nationality)
            # # update user details
            # TODO: update user details
            message = {
                'email': user['email'],
                'name': user['name'],
                'mobile': user['mobile'],
                'nationality': user['nationality']
            }
            return render_template('test-profile.html',  message=message)

    else:
        return redirect(url_for("login"))
# logout route
@app.route('/logout', methods=["POST", "GET"])
def logout():
    if "email" in session:
        db.users.find_one_and_update({'email': session['email']}, {
                                     '$set': {'isOnline': False}})
        session.pop("email", None)
        return redirect('/')
    else:
        return render_template('signup.html')


@app.route('/schedule', methods=["POST", "GET"])
def schedule():
    return render_template('schedule.html')


@app.route('/abstract_submission', methods=["POST", "GET"])
def abstract_submission():
    return render_template('abstract_submission.html')

# test route - get users
@app.route('/users', methods=['GET'])
def get_users():
    userList = []
    for user in users.find():
        userDict = {
            'name': user['name'],
            'email': user['email']
        }
        userList.append(userDict)

    # return list of users in json
    return jsonify(userList)

@app.route('/home-test', methods=['GET'])
def home_test():
    return render_template('home-test')

# test route - files upload
@app.route('/test-upload', methods=['GET'])
def test_upload_page():
    return '''
        <form action="/test-upload-file" method="POST" enctype="multipart/form-data">
            <label for="name">Name</label>
            <input type="text" name="name">

            <label for="file">Upload File</label>
            <input type="file" name="file">
            <input type="submit">
        </form>
    '''

@app.route('/test-upload-file', methods=['POST'])
def test_upload():
    # if 'file' in request.files:
    # # uploaded_file=request.files.get("file") or 
    # uploaded_file= None
    # buffer_memory=BytesIO()
    # uploaded_file.save(buffer_memory)

    # media_body=MediaIoBaseUpload(uploaded_file, uploaded_file.mimetype, resumable=True)
    # created_at= datetime.now().strftime("%Y%m%d%H%M%S")
    # file_metadata={
    #     "name":f"{uploaded_file.filename} ({created_at})",
    #     "appProperties":{
    #         "file_description":request.form.get("description")
    #     }
    # }

    # returned_fields="id, name, mimeType, webViewLink, exportLinks, appProperties"
    
    # upload_response=service.files().create(
    #     body = file_metadata, 
    #     media_body=media_body,  
    #     fields=returned_fields
    # ).execute()

    return 'test'


# @app.get('/gdrive-files')
# def getFileListFromGDrive():
#     selected_fields="files(id,name,webViewLink)"
#     gdrive_service=GoogleDriveService().build()
#     list_file=gdrive_service.files().list(fields=selected_fields).execute()
#     return {"files":list_file.get("files")}