from app import app
from flask import Flask, render_template
from flask import session
from flask import redirect
from flask import url_for

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
  # session.pop('loggedin', None)
   #session.pop('id', None)
   #session.pop('username', None)
   #session.pop('role', None)
   # Redirect to login page
   return redirect(url_for('home'))