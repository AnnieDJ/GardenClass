# This is for storing common functions that we use
from app import connect
import mysql.connector
from flask_hashing import Hashing

hashing = Hashing()

dbconn = None
connection = None
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, auth_plugin='mysql_native_password',\
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn