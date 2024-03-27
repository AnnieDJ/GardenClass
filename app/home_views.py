from app import app
from flask import Flask, render_template
from flask import session,request, redirect,url_for
from app import utils
import re
from datetime import datetime

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')
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

        user_id = ''
        if user is not None:
            role = user['role']
            if role == 'Member':
                cursor.execute("SELECT member_id FROM member WHERE user_name = %s", (username,))
                result = cursor.fetchone()
                user_id = result['member_id']
            elif role == 'Manager':
                cursor.execute("SELECT manager_id FROM manager WHERE user_name = %s", (username,))
                result = cursor.fetchone()
                user_id = result['manager_id']
            elif role == 'Instructor':
                cursor.execute("SELECT instructor_id FROM instructor WHERE user_name = %s", (username,))
                result = cursor.fetchone()
                user_id = result['instructor_id']
            else:
                msg = 'Invalid User'
                return render_template('login.html', msg=msg)

            #user_id = cursor.fetchone()['user_id']
            #account = user[:4] + (user_id,)
            #password = account[2]

           # user = cursor.fetchone()
            password = user['password']

            if utils.hashing.check_value(password, user_password, salt='schwifty'):
                session['loggedin'] = True
                session['id'] = user_id
                session['username'] = user['user_name']
                session['role'] = user['role']

                if role == 'Member':
                    return redirect(url_for('member_dashboard'))
                elif role == 'Instructor':
                    return redirect(url_for('instructor_dashboard'))
                elif role == 'Manager':
                    return redirect(url_for('manager_dashboard_different'))
            else:
                msg ='Invalid Password!'
        else:
            msg ='Invalid Username!'
    
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = session.pop('msg', None)
    if request.method == 'POST':
        # Form submitted, process the data
        username  = request.form['user_name']
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
    
        # Validation checks
        if not all(request.form.values()):
            msg = 'Please fill out all the fields!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', request.form['email']):
            msg = 'Invalid email address!'
        elif not re.match(r'^\d{9,12}$', request.form['phone']):
            msg = 'Invalid phone number!'
        elif utils.register_age_validation(date_of_birth):
            msg = 'member should be over 16 years old!'
        # Additional validation checks...

        elif not msg:
            # Data is valid, proceed with registration
            cursor = utils.getCursor()
            cursor.execute('SELECT * FROM member WHERE user_name = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                session.clear()
                session['user_name'] = request.form['user_name']
                session['title'] = request.form['title']
                session['firstname'] = request.form['first_name']
                session['lastname'] = request.form['last_name']
                session['phone'] = request.form['phone']
                session['email'] = request.form['email']
                session['address'] = request.form['address']
                session['date_of_birth'] = request.form['date_of_birth']
                
                password = request.form['confirm_password']
                hashed = utils.hashing.hash_value(password, salt='schwifty')
                session['confirm_password'] = hashed
            
                return redirect(url_for('bank_info'))

        elif request.method == 'POST':
             # Form is empty... (no POST data)
             msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('/register/register.html', msg=msg)

@app.route('/bank_info', methods=['GET', 'POST'])
def bank_info():
    msg = session.pop('msg', None)
    
    if request.method == 'POST':
        
        # Validation checks
        if not all(request.form.values()):
            msg = 'Please fill out all the fields!'
        elif not re.match(r'^\d{16}$', request.form['bank_card']):
            msg = 'Invalid bank card!'
        elif not re.match(r'^\d{3}$', request.form['security_code']):
            msg = 'Invalid Security Code!'
        
        elif not msg:    
            # Process bank information form        
            session['bank_name'] = request.form['bank_name']
            session['bank_card'] = request.form['bank_card']
            session['security_code'] = request.form['security_code']
            
            # Redirect to the final step or any other step
            return redirect(url_for('payment'))
    
        elif request.method == 'POST':
             # Form is empty... (no POST data)
             msg = 'Please fill out the form!'
             
    return render_template('/register/bank_info.html', msg=msg)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    # Retrieve user information from session
    if request.method == 'POST':
       pay_now = request.form['pay_now']
       
       cursor = utils.getCursor()
       cursor.execute('INSERT INTO member (user_name, title, first_name, last_name, position, phone_number, email, address, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (session['user_name'], session['title'], session['firstname'],session['lastname'],'Member',session['phone'], session['email'], session['address'], session['date_of_birth']))
       user_id =cursor.lastrowid
       cursor.execute('INSERT INTO user (user_name, password, role, related_member_id) VALUES (%s, %s, %s, %s)',(session['user_name'], session['confirm_password'],'Member',user_id))
       cursor.execute('INSERT INTO bank_info (bank_name,bank_card,security_code,member_id) VALUES (%s, %s, %s, %s)',(session['bank_name'],session['bank_card'],session['security_code'],user_id))
    
       if pay_now == 'Yes':
             pay_type = request.form['pay_type']
             if pay_type == 'Annual':
                #Annual pay
                pay_amount = 1000
                expiry_date = utils.one_year_later()
             else:
                 #Monthly Pay
                pay_amount = 100
                expiry_date_origin = utils.one_month_later()
                expiry_date = datetime(expiry_date_origin.year, expiry_date_origin.month, expiry_date_origin.day)
                
             payment_date = utils.current_date_time()
            
             cursor.execute('INSERT INTO payments (user_id,amount,payment_type,payment_date,status) VALUES (%s,%s,%s,%s,%s)',(user_id,pay_amount,'Subscription',payment_date,'Completed'))
             cursor.execute('INSERT INTO subscriptions (user_id,type,start_date,end_date,status) VALUES (%s,%s,%s,%s,%s)',(user_id,pay_type,payment_date,expiry_date,'Active'))
             # Clear session data after registration
             session.clear()
             return redirect(url_for('home'))
    
    return render_template('/register/payment.html')


@app.route('/password', methods=['GET', 'POST'])
def password():
    if 'loggedin' in session and session['loggedin']:
        msg = request.args.get('msg', '') 
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM user WHERE user_id = %s', (session['id'],))
        user_data = cursor.fetchone()
        return render_template('password.html', user_data=user_data, msg=msg,role=session['role'])
    return redirect(url_for('login'))


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'loggedin' in session and session['loggedin']:
        msg = ''
        current_password = request.form.get('currentpassword')
        new_password = request.form.get('newpassword')
        confirm_password = request.form.get('confirmpassword')

        cursor = utils.getCursor()
        cursor.execute('SELECT password FROM user WHERE user_id = %s', (session['id'],))
        result = cursor.fetchone()

        if result:
            if not utils.hashing.check_value(result[0], current_password, salt='schwifty'):
                msg = 'Current password is incorrect'
            elif new_password != confirm_password:
                msg = 'New password and confirm password do not match'
            elif len(new_password) < 8:
                msg = 'New password must be at least 8 characters long'
            elif not re.search(r'\d', new_password):
                msg = 'New password must contain at least one digit'
            elif not re.search(r'[A-Za-z]', new_password):
                msg = 'New password must contain at least one letter'
            elif not re.search(r'[^A-Za-z0-9]', new_password):
                msg = 'New password must contain at least one special character'
            else:
                hashed_new_password = utils.hashing.hash_value(new_password, salt='schwifty')
                cursor.execute('UPDATE user SET password = %s WHERE id = %s', (hashed_new_password, session['id']))
                utils.connection.commit()
                msg = 'Password updated successfully!'
                return redirect(url_for('password', msg=msg)) 

        else:
            msg = 'User not found'

        return render_template('password.html', msg=msg, role=session['role'])
    
    return redirect(url_for('login'))



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('role', None)
   # Redirect to login page
   return redirect(url_for('home'))

