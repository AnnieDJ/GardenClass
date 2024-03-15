from app import app
from flask import Flask, render_template
from flask import session,request, redirect,url_for
from app import utils
from datetime import date

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the message exists in the session
    msg = session.pop('msg', None)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_password = request.form['password']

        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM user WHERE user_name = %s", (username,))
        user = cursor.fetchone()

        if user is not None:
            role = user[3]
            if role == 'Member':
                cursor.execute("SELECT member_id FROM member WHERE user_name = %s", (username,))
            elif role == 'Manager':
                cursor.execute("SELECT manager_id FROM manager WHERE user_name = %s", (username,))
            elif role == 'Instructor':
                cursor.execute("SELECT instructor_id FROM instructor WHERE user_name = %s", (username,))
            else:
                msg = 'Invalid User'
                return render_template('login.html', msg=msg)

            user_id = cursor.fetchone()[0]
            account = user[:4] + (user_id,)
            password = account[2]

            if utils.hashing.check_value(password, user_password, salt='schwifty'):
                session['loggedin'] = True
                session['id'] = account[4]
                session['username'] = account[1]
                session['role'] = account[3]

                if role == 'Member':
                    return redirect(url_for('member_dashboard'))
                elif role == 'Instructor':
                    return redirect(url_for('instructor_dashboard'))
                elif role == 'Manager':
                    return redirect(url_for('manager_dashboard'))
            else:
                msg ='Invalid Password!'
        else:
            msg ='Invalid Username!'
    
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('role', None)
   # Redirect to login page
   return redirect(url_for('home'))