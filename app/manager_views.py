from app import app
from flask import render_template
from flask import session

@app.route("/manager/dashboard")
def manager_dashboard():
    if 'loggedin' in session and session['loggedin']:
        return render_template("/manager/managerdashboard.html", username=session['username'], role=session['role'])

@app.route("/manager/profile")
def manager_profile():
    return "Manager Profile"