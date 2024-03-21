# This is for storing common functions that we use
from app import connect
import mysql.connector
from flask_hashing import Hashing
from app import app
from datetime import datetime, timedelta

hashing = Hashing()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.secret_key = 'secret key of neal first assessment'

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def current_date_time():
    return datetime.now()
def one_month_later():
    
    current_datetime = datetime.now()
    
    days_in_current_month = (current_datetime.replace(day=1) + timedelta(days=32)).day

    one_month_later = current_datetime.replace(day=min(current_datetime.day, days_in_current_month)) + timedelta(days=32)
    
    return one_month_later

def one_year_later():
    
    current_date = datetime.now()
    
    one_year_later = current_date + timedelta(days=365)
    
    return one_year_later