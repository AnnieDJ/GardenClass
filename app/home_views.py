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
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        user_password = request.form['password']
        
        #using for debug loggin function
        hashed = utils.hashing.hash_value(user_password,salt='schwifty')
        
        cursor = utils.getCursor()
        
        cursor.execute("SELECT * FROM user WHERE user_name = %s", (username,))
        user = cursor.fetchone()
        
        if user is not None and user[3] == "Member":
             cursor.execute("SELECT member_id FROM member WHERE user_name = %s", (username,))
        elif user is not None and user[3] == "Manager":
             cursor.execute("SELECT manager_id FROM manager WHERE user_name = %s", (username,))
        elif user is not None and user[3] == "Instructor":
             cursor.execute("SELECT instructor_id FROM instructor WHERE user_name = %s", (username,))
        else:
            msg = 'User does not exist'
            return render_template('login.html', msg=msg)
        
        user_id = cursor.fetchone()[0]        
        # Fetch one record and return result
        account = user[:4] + (user_id,)   
        password = account[2]
            
        if utils.hashing.check_value(password, user_password, salt='schwifty'):
            # If account exists in accounts table 
            # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[4]
                session['username'] = account[1]
                session['role'] = account[3]
                # Redirect to home page
            
                   # Redirect to appropriate home based on role
                if account[3] == 'Member':
                     return redirect(url_for('member_dashboard'))
                elif account[3] == 'Instructor':
                    return redirect(url_for('instructor_dashboard'))
                elif account[3] == 'Manager':
                    return redirect(url_for('manager_dashboard'))
                else:
                     return render_template('login.html', message='Invalid credentials')
        else:
           #password incorrect
            msg ='Invalid Password!'
        
    else:
        # Account doesn't exist or username incorrect
        msg = 'Invalid Username'
    # Show the login form with message (if any)
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