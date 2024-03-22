from app import app
from flask import render_template,redirect,request,url_for
from flask import session
from flask import flash,get_flashed_messages
from datetime import datetime
from app import utils
import base64


@app.route('/instructor/dashboard')
def instructor_dashboard():
     if 'loggedin' in session and session['loggedin']:
         return render_template("/instructor/instr_dashboard.html", username=session['username'], role=session['role'])

@app.route('/instructor/profile')
def instructor_profile():
    if 'loggedin' in session and session['loggedin']:
        messages = get_flashed_messages()
        encoded_instructor_profile = []

        cursor = utils.getCursor()
        instructorquery = "SELECT * FROM instructor WHERE instructor_id = %s;"
        cursor.execute(instructorquery ,(session['id'],))
        instructor = cursor.fetchone()
        
        if instructor[10] is not None and instructor[10] != '':
            image_encode = base64.b64encode(instructor[11]).decode('utf-8')
            encoded_instructor_profile.append((instructor[0], instructor[1],instructor[2] ,instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],image_encode))
        else:
            encoded_instructor_profile.append((instructor[0], instructor[1],instructor[2],instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],None))
            
        
        
        return render_template('/instructor/instr_profile.html', messages=messages, account=encoded_instructor_profile, role=session['role'])
       
    else:
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

            if role == 'Instructor':
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
