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
        cursor = utils.getCursor()

        # Retrieve the current logged-in user's username
        user_name = session['username']
        
        # First, get the related_instructor_id from the User table
        cursor.execute("SELECT related_instructor_id FROM User WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()  # Assuming each username uniquely corresponds to one related_instructor_id
        if result is None:
            cursor.close()
            return "Instructor ID not found for the current user", 404  # Or redirect to an error page

        related_instructor_id = result['related_instructor_id']

        # Then, use the related_instructor_id to query the lessons table
        cursor.execute("SELECT * FROM lessons WHERE instructor_id = %s ORDER BY date, start_time LIMIT 1", (related_instructor_id,))
        lesson_data = cursor.fetchall()

        cursor.execute("SELECT * FROM workshops ORDER BY date, start_time LIMIT 2")
        workshop_data = cursor.fetchall()

        cursor.execute("SELECT * FROM news ORDER BY date_published LIMIT 1")
        news_data = cursor.fetchall()
      
        cursor.close()
        return render_template("instructor/instr_dashboard.html", lessons=lesson_data, workshops=workshop_data, news=news_data, username=user_name, role=session['role'])
  
    else:
        return redirect(url_for('login'))


@app.route('/instructor/lessons')
def instructor_lessons():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        user_name = session['username']
        
        cursor.execute("SELECT related_instructor_id FROM User WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            return "Instructor ID not found for the current user", 404

        related_instructor_id = result['related_instructor_id']

       
        cursor.execute("SELECT * FROM lessons WHERE instructor_id = %s", (related_instructor_id,))
        lessons_data = cursor.fetchall()
      
        cursor.close()
        return render_template("/instructor/instr_lessons.html", lessons=lessons_data)
    else:
        return redirect(url_for('login'))


      
        # Make sure the username and role are set in the session as well
        
@app.route('/instructor/profile')
def instructor_profile():
    if 'loggedin' in session and session['loggedin']:
        messages = get_flashed_messages()
        encoded_instructor_profile = []

        cursor = utils.getCursor()
        instructorquery = "SELECT * FROM instructor WHERE instructor_id = %s;"
        cursor.execute(instructorquery ,(session['id'],))
        instructor = cursor.fetchone()
        
        if instructor['instructor_image_name'] is not None and instructor['instructor_image_name'] != '':
            image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
            encoded_instructor_profile.append((instructor['instructor_id'], instructor['user_name'],instructor['title'] ,instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],image_encode))
        else:
            encoded_instructor_profile.append((instructor['instructor_id'], instructor['user_name'],instructor['title'],instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],None))
            
        
        
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
