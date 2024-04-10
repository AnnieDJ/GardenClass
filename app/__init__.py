from flask import Flask

app = Flask(__name__)

app.secret_key = 'the first secret key for schwifty'

from app import member_views
from app import manager_views
from app import instructor_views
from app import home_views
from app import payment_views
from app import location_views
from app import booking_views
from app import news_views
