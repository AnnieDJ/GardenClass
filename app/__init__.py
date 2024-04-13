from flask import Flask

app = Flask(__name__)

app.secret_key = 'the first secret key for schwifty'

app.config['UPLOAD_FOLDER'] = 'app/static/workshops_images'  # Define where to store the uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed upload file extensions


from app import member_views
from app import manager_views
from app import instructor_views
from app import home_views
from app import payment_views
from app import location_views
from app import booking_views
from app import news_views
