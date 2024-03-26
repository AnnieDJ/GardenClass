from app import app
from flask import render_template,redirect,request,url_for
from flask import session
from flask import flash,get_flashed_messages
from datetime import datetime
from app import utils
from werkzeug.utils import secure_filename
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
        # Retrieve filter values from query parameters
        status = request.args.get('status', default=None, type=str)
        date = request.args.get('date', default=None, type=str)
        member_id = request.args.get('member_id', default=None, type=int)

        cursor.execute("SELECT related_instructor_id FROM User WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            return "Instructor ID not found for the current user", 404

        related_instructor_id = result['related_instructor_id']

        # Start building the query with no filters
        query = "SELECT * FROM lessons WHERE instructor_id = %s"
        query_params = [related_instructor_id]

        # Append filters to the query if they are provided
        if status:
            query += " AND status = %s"
            query_params.append(status)
        if date:
            query += " AND date = %s"
            query_params.append(date)
        if member_id is not None:  # checking if it's not None because 0 is a valid ID but falsy
            query += " AND member_id = %s"
            query_params.append(member_id)

        # Add ordering by date and start time
        query += " ORDER BY date, start_time"

        # Execute the built query
        cursor.execute(query, query_params)
        lessons_data = cursor.fetchall()

        cursor.close()
        return render_template("/instructor/instr_lessons.html", lessons=lessons_data, role=session['role'])
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
        cursor.execute(instructorquery, (session['id'],))
        instructor = cursor.fetchone()

        if instructor['instructor_image']:
            image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
        
        encoded_instructor_profile.append((
            instructor['instructor_id'], instructor['user_name'], instructor['title'], instructor['first_name'],
            instructor['last_name'], instructor['position'], instructor['phone_number'], instructor['email'],
            instructor['address'], instructor['instructor_profile'], image_encode
        ))

        return render_template('/instructor/instr_profile.html', messages=messages, account=encoded_instructor_profile, role=session['role'])
    else:
        return redirect(url_for('login'))



@app.route('/instructor/editinstrprofile', methods=['GET', 'POST'])
def editinstrprofile():
    if 'loggedin' in session and session['loggedin']:
        messages = get_flashed_messages()
        cursor = utils.getCursor()
        image_encode = None
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            address = request.form.get('address')
            instructor_profile = request.form.get('instructor_profile')
            instructor_image = request.files.get('instructor_image')

            if instructor_image:
                if utils.allowed_file(instructor_image.filename):
                    image_data = instructor_image.read()
                    image_encode = base64.b64encode(image_data).decode('utf-8')

                    cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, instructor_profile = %s, instructor_image = %s WHERE user_name = %s",
                                    (title, first_name, last_name, position, phone_number, email, address, instructor_profile, image_data, session['username'],))
                    flash('Profile updated successfully with image')
                else:
                    flash('Invalid file type, please upload a valid image file')
            else:
                cursor.execute("SELECT instructor_image FROM instructor WHERE user_name = %s", (session['username'],))
                row = cursor.fetchone()
                if row and row['instructor_image']:
                    image_encode = base64.b64encode(row['instructor_image']).decode('utf-8')


            cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, instructor_profile = %s WHERE user_name = %s",
                            (title, first_name, last_name, position, phone_number, email, address, instructor_profile, session['username'],))
            flash('Profile updated successfully without image')

            return redirect(url_for('instructor_profile'))

        else:
            cursor.execute("SELECT * FROM instructor WHERE user_name = %s", (session['username'],))
            instructor = cursor.fetchone()
            return render_template('/instructor/edit_instr_profile.html', instructor=instructor, messages=messages, image_encode=image_encode,role=session['role'])
    else:
        return redirect(url_for('login'))



@app.route('/instructor/workshops')
def instructor_workshops():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        # ... Code to retrieve workshops data ...
        
        return render_template('instructor/instr_workshops.html', workshops=workshops_data)
    else:
        return redirect(url_for('login'))
