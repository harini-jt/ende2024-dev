# connect to database
import os
import pymongo

# set the database name
def connect_db():
    try:
        client = pymongo.MongoClient(os.environ.get('MONGO_URI'))
        db = client.get_database(os.environ.get('DB_NAME'))
        users = db[os.environ.get('USERS_COLLECTION')]

        return {'message': True, 'users': users, 'db': db, 'client': client}
    except Exception as e:
        return 'MongoDB Connection Error: ' + str(e)

def isAdmin(role):
    if role == os.environ.get('ADMIN_ROLE'):
        return True
    elif role == '1':
        return False
    else:
        return False
