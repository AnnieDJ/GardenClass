from app import app
from flask import Flask, render_template

@app.route('/')
def login():
    return render_template('login.html')


@app.route("/member/dashboard")
def member_dashboard():
    return "Member Dashboard"

@app.route("/member/profile")
def member_profile():
    return "Member Profile"