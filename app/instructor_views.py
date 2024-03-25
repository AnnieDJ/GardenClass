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
        cursor.execute("SELECT related_instructor_id FROM user WHERE user_name = %s", (user_name,))
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
        # Retrieve filter values from query parameters
        status = request.args.get('status', default=None, type=str)
        date = request.args.get('date', default=None, type=str)
        member_id = request.args.get('member_id', default=None, type=int)

        # Get instructor ID based on logged in user
        cursor.execute("SELECT related_instructor_id FROM user WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            return "Instructor ID not found for the current user", 404
        related_instructor_id = result['related_instructor_id']

        # Modified query to fetch one-on-one lessons and join with the member table
        ool_query = """
        SELECT ool.*, m.first_name, m.last_name, m.user_name 
        FROM `one-on-one lessons` ool
        JOIN `member` m ON ool.member_id = m.member_id 
        WHERE ool.instructor_id = %s
       """

       
        ool_params = [related_instructor_id]

        if status:
            ool_query += " AND ool.status = %s"
            ool_params.append(status)
        if date:
            ool_query += " AND ool.date = %s"
            ool_params.append(date)
        if member_id is not None:
            ool_query += " AND ool.member_id = %s"
            ool_params.append(member_id)

        ool_query += " ORDER BY ool.date, ool.start_time"
        cursor.execute(ool_query, tuple(ool_params))
        one_on_one_lessons_data = cursor.fetchall()

        # Assuming group lessons query remains unchanged
        lessons_query = "SELECT * FROM `lessons` WHERE instructor_id = %s"
        lessons_params = [related_instructor_id]

        if date:
            lessons_query += " AND date = %s"
            lessons_params.append(date)

        lessons_query += " ORDER BY date, start_time"
        cursor.execute(lessons_query, tuple(lessons_params))
        group_lessons_data = cursor.fetchall()

        cursor.close()
        return render_template(
            "/instructor/instr_lessons.html",
            one_on_one_lessons=one_on_one_lessons_data,
            group_lessons=group_lessons_data,
            role=session['role']
        )
    else:
        return redirect(url_for('login'))



      
        # Make sure the username and role are set in the session as well
        
@app.route('/instructor/profile')
def instructor_profile():
    if 'loggedin' in session and session['loggedin']:
        
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
            
        
        
        return render_template('instructor/instr_profile.html', account=encoded_instructor_profile, role=session['role'])
       
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
            #cursor = utils.getCursor()

            #if role == 'Instructor':
                #cursor.execute('UPDATE agronomists SET first_name = %s, family_name = %s, email = %s, phone = %s , address = %s WHERE id = %s',
                               #(new_firstname, new_familyname, new_email, new_phone, new_address, session['id']))
            #else:
               # cursor.execute('UPDATE staff_admin SET first_name = %s, family_name = %s, email = %s, phone = %s WHERE id = %s',
                               #(new_firstname, new_familyname, new_email, new_phone, session['id']))

            #utils.connection.commit()
            #msg = 'Profile updated successfully!'
        #else:
            #msg = 'User not logged in'
        #flash(msg, 'success' if 'loggedin' in session else 'error')
    return redirect(url_for('profile'))



@app.route('/instructor/workshops')
def instructor_workshops():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        instructor_id = request.args.get('instructor_id')
        date = request.args.get('date')
        location_id = request.args.get('location_id')  # Updated variable name to match column
        
        query = """
        SELECT w.*, i.first_name, i.last_name FROM workshops w
        JOIN instructor i ON w.instructor_id = i.instructor_id
        """
        
        params = []
        conditions = []
        
        if instructor_id:
            conditions.append("w.instructor_id = %s")
            params.append(instructor_id)
        if date:
            conditions.append("w.date = %s")
            params.append(date)
        if location_id:
            conditions.append("w.location_id = %s")  # Corrected to use the accurate column name
            params.append(location_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY w.date"
        
        cursor.execute(query, tuple(params))  # Execute the query with parameters
        workshops_data = cursor.fetchall()
        
        return render_template('instructor/instr_workshops.html', workshops=workshops_data, role=session['role'])
    else:
        return redirect(url_for('login'))
