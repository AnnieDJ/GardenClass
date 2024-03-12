from flask import Flask

app = Flask(__name__)

from app import member_views
from app import manager_views
from app import instructor_views
from app import home_views