from app import app
from flask import render_template

@app.route("/member/dashboard")
def member_dashboard():
    return render_template('memberdashboard.html')

@app.route("/member/profile")
def member_profile():
    return "Member Profile"