from app import app
from flask import render_template
from flask import session

@app.route("/instructor/dashboard")
def instructor_dashboard():
     if 'loggedin' in session and session['loggedin']:
         return render_template("/instructor/instructordashboard.html", username=session['username'], role=session['role'])

@app.route("/instructor/profile")
def instructor_profile():
    return "instructor Profile"