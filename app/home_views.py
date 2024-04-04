from app import app
from flask import Flask, render_template, flash
from flask import session,request, redirect,url_for
from app import utils
import re
from datetime import datetime




## View All Instuctor Images on HomePage##
def get_all_instructors():
    cursor = utils.getCursor()
    
    # Fetch all instructor details
    cursor.execute("SELECT user_name, first_name, last_name FROM garden_club.instructor")
    instructors = cursor.fetchall()
    cursor.close()
    
    # Append the path to the instructor's image URL
    for instructor in instructors:
        first_name = instructor['user_name'].split('_')[0].lower()
        image_filename = f"instr_{first_name}.jpg"
        instructor['image_src'] = url_for('static', filename=f'img/instructors/{image_filename}')
        
    return instructors



## Home Page ##
@app.route('/')
@app.route('/home')
def home():
    instructor_data = get_all_instructors()
    return render_template('index.html', instructors=instructor_data)



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
                    return redirect(url_for('manager_dashboard'))
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


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'loggedin' not in session or not session['loggedin']:
        return redirect(url_for('login'))

    # Retrieve form data
    current_password = request.form.get('currentpassword')
    new_password = request.form.get('newpassword')
    confirm_password = request.form.get('confirmpassword')

    cursor = utils.getCursor()
    user_id = session['id']

    # Select the current password from the database based on role
    role_specific_query = {
        'Member': 'SELECT password FROM user WHERE related_member_id = %s AND role = %s',
        'Manager': 'SELECT password FROM user WHERE related_manager_id = %s AND role = %s',
        'Instructor': 'SELECT password FROM user WHERE related_instructor_id = %s AND role = %s'
    }.get(session.get('role'))

    if not role_specific_query:
        flash("User role is not recognized.", "danger")
        return redirect(url_for('login'))

    cursor.execute(role_specific_query, (user_id, session.get('role')))
    result = cursor.fetchone()

    # Initialize hashed_new_password variable
    hashed_new_password = None

    if result is None:
        flash('No record found associated with this user ID', 'danger')
    elif not utils.hashing.check_value(result['password'], current_password, salt='schwifty'):
        flash('Current password is incorrect', 'danger')
    elif new_password != confirm_password:
        flash('New password and confirm password do not match', 'danger')
    elif len(new_password) < 8:
        flash('New password must be at least 8 characters long', 'danger')
    elif not re.search(r'\d', new_password):
        flash('New password must contain at least one digit', 'danger')
    elif not re.search(r'[A-Za-z]', new_password):
        flash('New password must contain at least one letter', 'danger')
    elif not re.search(r'[^A-Za-z0-9]', new_password):
        flash('New password must contain at least one special character', 'danger')
    else:
        # All checks have passed, update the password
        hashed_new_password = utils.hashing.hash_value(new_password, salt='schwifty')

    # Update the user's password in the database based on role
    if hashed_new_password:
        if session.get('role') == 'Member':
            cursor.execute('UPDATE user SET password = %s WHERE related_member_id = %s AND role = %s', (hashed_new_password, user_id, 'Member'))
        elif session.get('role') == 'Manager':
            cursor.execute('UPDATE user SET password = %s WHERE related_manager_id = %s AND role = %s', (hashed_new_password, user_id, 'Manager'))
        elif session.get('role') == 'Instructor':
            cursor.execute('UPDATE user SET password = %s WHERE related_instructor_id = %s AND role = %s', (hashed_new_password, user_id, 'Instructor'))
        utils.connection.commit()
        flash('Password updated successfully!')

    # Redirect user to the appropriate profile page
    redirect_route = {
        'Member': 'member_profile',
        'Manager': 'manager_profile',
        'Instructor': 'instructor_profile'
    }.get(session.get('role'), 'login')  # Fallback to 'login' if role is not found
    
    return redirect(url_for(redirect_route))



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('role', None)
   # Redirect to login page
   return redirect(url_for('home'))

