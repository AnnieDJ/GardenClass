from app import app
from flask import render_template,redirect,request,url_for
from flask import session
from flask import flash,get_flashed_messages
from datetime import datetime
from app import utils


@app.route('/instructor/dashboard')
def instructor_dashboard():
     if 'loggedin' in session and session['loggedin']:
         return render_template("/instructor/instr_dashboard.html", username=session['username'], role=session['role'])

@app.route('/instructor/profile')
def instructor_profile():
    if 'loggedin' in session:
        messages = get_flashed_messages()

        role = session.get('role', 'unknown')

        if role == 'Instructor':
            cursor = utils.getCursor()
            instructorquery = "SELECT * FROM instructor WHERE user_id = %s;"
            cursor.execute(agronomistquery ,(session['id'],))
            agronomist = cursor.fetchone()
            return render_template('instr_profile.html', messages=messages, agronomist=agronomist)
        elif role == 'Manager':
            cursor = utils.getCursor()
            agronomistquery = "SELECT * FROM agronomists WHERE id = %s;"
            cursor.execute(agronomistquery ,(session['id'],))
            agronomist = cursor.fetchone()
            return render_template('agronomistprofile.html', messages=messages, agronomist=agronomist)
        elif role == 'Manager':
            cursor = utils.getCursor()
            cursor.execute('SELECT * FROM staff_admin WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            return render_template('profile.html', account=account, messages=messages)
        else:
           msg = 'Invalid User'
           return render_template('login.html', msg=msg)

    return redirect(url_for('login'))


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if request.method == "POST":
        msg = ''
        if 'loggedin' in session:
            new_firstname = request.form.get('firstname')
            new_familyname = request.form.get('familyname')
            new_email = request.form.get('email')
            new_phone = request.form.get('phone')
            new_address = request.form.get('address')
            role = session.get('role', 'unknown')  
            cursor = utils.getCursor()

            if role == 'agronomist':
                cursor.execute('UPDATE agronomists SET first_name = %s, family_name = %s, email = %s, phone = %s , address = %s WHERE id = %s',
                               (new_firstname, new_familyname, new_email, new_phone, new_address, session['id']))
            else:
                cursor.execute('UPDATE staff_admin SET first_name = %s, family_name = %s, email = %s, phone = %s WHERE id = %s',
                               (new_firstname, new_familyname, new_email, new_phone, session['id']))

            utils.connection.commit()
            msg = 'Profile updated successfully!'
        else:
            msg = 'User not logged in'
        flash(msg, 'success' if 'loggedin' in session else 'error')
    return redirect(url_for('profile'))
