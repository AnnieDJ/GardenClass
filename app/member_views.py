from app import app
from flask import render_template
from flask import session

@app.route("/member/dashboard")
def member_dashboard():
    if 'loggedin' in session and session['loggedin']:
        return render_template('/member/memberdashboard.html', username=session['username'], role=session['role'])

@app.route("/member/profile")
def member_profile():
    return "Member Profile"