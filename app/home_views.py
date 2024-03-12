from app import app
from flask import Flask, render_template

@app.route('/')
def home():
    return render_template('base.html')
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    return "Log Out"