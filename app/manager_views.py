from app import app
from flask import render_template

@app.route("/manager/dashboard")
def manager_dashboard():
    return render_template("/manager/managerdashboard.html")

@app.route("/manager/profile")
def manager_profile():
    return "Manager Profile"