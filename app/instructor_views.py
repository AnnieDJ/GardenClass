from app import app
from flask import render_template

@app.route("/instructor/dashboard")
def instructor_dashboard():
    return render_template("/instructor/instructordashboard.html")

@app.route("/instructor/profile")
def instructor_profile():
    return "instructor Profile"