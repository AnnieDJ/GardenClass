from app import app
from flask import render_template,redirect,request,url_for
from flask import session
from flask import flash,get_flashed_messages
from datetime import datetime
from app import utils
from werkzeug.utils import secure_filename
import base64
from flask import jsonify
import re


@app.context_processor
def inject_instructor_details():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        user_name = session.get('username')

        # Fetch the instructor details based on the session's username
        cursor.execute("""
        SELECT i.first_name, i.last_name, i.email, i.instructor_image
        FROM instructor i
        JOIN user u ON i.instructor_id = u.related_instructor_id
        WHERE u.user_name = %s
        """, (user_name,))
        instructor_info = cursor.fetchone()
        cursor.close()

        if instructor_info:
            full_name = f"{instructor_info['first_name']} {instructor_info['last_name']}"
            email = instructor_info['email']
            # Check if an image is present; if not, use the placeholder URL
            if instructor_info['instructor_image']:
                image_encode = base64.b64encode(instructor_info['instructor_image']).decode('utf-8')
                image_src = f"data:image/jpeg;base64,{image_encode}"
            else:
                image_src = "https://i.pinimg.com/564x/92/5c/52/925c52543aa8096c66214311fa598fbc.jpg"

            return {
                'instructor_name': full_name,
                'instructor_email': email,
                'instructor_image_src': image_src
            }
    return {}




## Instructor Dashboard ##
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
        cursor.execute("SELECT lessons.*,locations.name,locations.address \
                        FROM lessons \
                        JOIN locations \
                        ON lessons.location_id = locations.location_id \
                       WHERE instructor_id = %s ORDER BY date, start_time LIMIT 1", (related_instructor_id,))
        lesson_data = cursor.fetchall()

        cursor.execute("SELECT * FROM workshops ORDER BY date, start_time LIMIT 2")
        workshop_data = cursor.fetchall()

        cursor.execute("SELECT * FROM news ORDER BY date_published LIMIT 1")
        news_data = cursor.fetchall()
      
        cursor.close()
        return render_template("instructor/instr_dashboard.html", lessons=lesson_data, workshops=workshop_data, news=news_data, username=user_name, role=session['role'])
  
    else:
        return redirect(url_for('login'))



## Instructor Lessons ##
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
        SELECT ool.*, m.first_name, m.last_name, m.user_name ,l.name,l.address
        FROM `one_on_one_lessons` ool
        JOIN `member` m ON ool.member_id = m.member_id 
        JOIN `locations` l ON ool.location_id = l.location_id 
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
        lessons_query =  """SELECT lessons.* , locations.name,locations.address
                            FROM lessons 
                            JOIN locations ON lessons.location_id = locations.location_id
                            WHERE instructor_id = %s 
                          """
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
        

## Instructor Edit Lesson ##
@app.route('/instructor/update_lesson/<int:lesson_id>', methods=['POST'])
def update_instructor_lesson(lesson_id):
    if 'loggedin' in session and session['loggedin'] and session['role'] == 'Instructor':

        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location_id = request.form.get('location_id')
        price = request.form.get('price')
        status = request.form.get('status')
        

        cursor = utils.getCursor()
        update_query = """
        UPDATE one_on_one_lessons
        SET date = %s, start_time = %s, end_time = %s, location_id = %s, status = %s, price = %s
        WHERE lesson_id = %s
        """
        cursor.execute(update_query, (date, start_time, end_time, location_id, status, price, lesson_id))
        cursor.connection.commit()
        

        if cursor.rowcount > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'No lesson updated.'})
    else:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401



@app.route('/instructor/update_group_lesson/<int:lesson_id>', methods=['POST'])
def update_group_lesson(lesson_id):
    if 'loggedin' in session and session['role'] == 'Instructor':

        title = request.form.get('title')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location_id = request.form.get('location_id')
        capacity = request.form.get('capacity')
        price = request.form.get('price')
        
        # Update database
        cursor = utils.getCursor()
        update_query = """
        UPDATE lessons
        SET  title = %s,date = %s, start_time = %s, end_time = %s, location_id = %s, capacity = %s, price = %s
        WHERE lesson_id = %s
        """
        cursor.execute(update_query, ( title, date, start_time, end_time, location_id, capacity, price, lesson_id))
        #cursor.connection.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'No group lesson updated.'})
    else:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

# API endpoint to get locations for dropdown
@app.route('/api/locations', methods=['GET'])
def api_locations():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute("SELECT location_id, name FROM locations;")
        locations = cursor.fetchall()
        cursor.close()
        return jsonify(locations)
    else:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    

@app.route('/api/members', methods=['GET'])
def api_members():
    if 'loggedin' in session:
        cursor = utils.getCursor()
        cursor.execute("SELECT member_id, first_name, last_name FROM member;")  # Adjust the query to match your schema
        members = cursor.fetchall()
        cursor.close()
        return jsonify(members)
    else:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    
@app.route('/instructor/add_lesson', methods=['POST'])
def add_lessons():
    # Check if the user is logged in
    if 'loggedin' in session:
        # Extract information from the form
        instructor_id = request.form.get('instructor_id')
        member_id = request.form.get('member_id')  # This will be used for one-on-one lessons
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        price = request.form.get('price')
        status = request.form.get('status', 'Scheduled')  # Default status for one-on-one
        capacity = request.form.get('capacity', type=int)  # For group lessons
        location_id = request.form.get('location_id')
        title = request.form.get('title')  # For group lessons
        lesson_type = request.form.get('lesson_type')  # 'group' or 'one_on_one'

        cursor = utils.getCursor()

        try:
            if lesson_type == 'group':
                # Check for existing group lesson
                cursor.execute("""SELECT * FROM lessons WHERE instructor_id = %s AND date = %s 
                                  AND start_time = %s AND end_time = %s AND location_id = %s 
                                  AND title = %s""",
                               (instructor_id, date, start_time, end_time, location_id, title))
            else:
                # Check for existing one-on-one lesson
                cursor.execute("""SELECT * FROM one_on_one_lessons WHERE instructor_id = %s 
                                  AND member_id = %s AND date = %s AND start_time = %s 
                                  AND end_time = %s AND location_id = %s""",
                               (instructor_id, member_id, date, start_time, end_time, location_id))

            lesson_exists = cursor.fetchone()
            if lesson_exists:
                return jsonify({'success': False, 'message': 'A similar lesson already exists.'})

            if lesson_type == 'group':
                # Insert group lesson
                cursor.execute("""INSERT INTO lessons (instructor_id, date, start_time, end_time, 
                                  capacity, location_id, title, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                               (instructor_id, date, start_time, end_time, capacity, location_id, title, price))
            else:
                # Insert one-on-one lesson
                cursor.execute("""INSERT INTO one_on_one_lessons (instructor_id, member_id, date, 
                                  start_time, end_time, price, status, location_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                               (instructor_id, member_id, date, start_time, end_time, price, status, location_id))

            # Your environment/setup needs to ensure data is committed here, if necessary
            return jsonify({'success': True, 'message': 'Lesson added successfully.'})
        except Exception as err:
            # Handle error
            return jsonify({'success': False, 'message': str(err)})
        finally:
            # Always ensure resources are cleaned up
            cursor.close()
    else:
        # User is not logged in
        return jsonify({'success': False, 'message': 'User is not logged in.'}), 401 

@app.route('/add_one_on_one_lesson',methods=['POST'])
def add_one_on_one_lesson():
    if 'loggedin' in session and session['loggedin']:
        instructor_id = request.form.get('instructor_id')
        member_id = request.form.get('member_id')  # This will be used for one-on-one lessons
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        price = request.form.get('price')
        status = request.form.get('status', 'Scheduled')  # Default status for one-on-one
        location_id = request.form.get('location_id')
        
        cursor = utils.getCursor()
        
        try:

          # Check for existing one-on-one lesson
            cursor.execute("""SELECT * FROM one_on_one_lessons WHERE instructor_id = %s 
                                  AND member_id = %s AND date = %s AND start_time = %s 
                                  AND end_time = %s AND location_id = %s""",
                               (instructor_id, member_id, date, start_time, end_time, location_id))

            lesson_exists = cursor.fetchone()
            if lesson_exists:
                return jsonify({'success': False, 'message': 'A similar lesson already exists.'})

            
           
            # Insert one-on-one lesson
            cursor.execute("""INSERT INTO one_on_one_lessons (instructor_id, member_id, date, 
                              start_time, end_time, price, status, location_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                              (session['id'], member_id, date, start_time, end_time, price, status, location_id))

            # Your environment/setup needs to ensure data is committed here, if necessary
            return jsonify({'success': True, 'message': 'Lesson added successfully.'})
        except Exception as err:
            # Handle error
            return jsonify({'success': False, 'message': str(err)})
        finally:
            # Always ensure resources are cleaned up
            cursor.close()
    else:
        # User is not logged in
        return jsonify({'success': False, 'message': 'User is not logged in.'}), 401
 

@app.route('/add_group_lesson',methods=['POST'])
def add_group_lessonn():
    if 'loggedin' in session and session['loggedin']:
        instructor_id = request.form.get('instructor_id')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        price = request.form.get('price')
        status = request.form.get('status', 'Scheduled')  # Default status for one-on-one
        capacity = request.form.get('capacity', type=int)  # For group lessons
        location_id = request.form.get('location_id')
        title = request.form.get('title')  # For group lessons
        
        cursor = utils.getCursor()
        
        try:

          # Check for existing group lesson
            cursor.execute("""SELECT * FROM lessons WHERE instructor_id = %s AND date = %s 
                            AND start_time = %s AND end_time = %s AND location_id = %s 
                            AND title = %s""",
                            (instructor_id, date, start_time, end_time, location_id, title))

            lesson_exists = cursor.fetchone()
            if lesson_exists:
                return jsonify({'success': False, 'message': 'A similar lesson already exists.'})

            
           
            # Insert group lesson
            cursor.execute("""INSERT INTO lessons (instructor_id, date, start_time, end_time, 
                            capacity, location_id, title, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                          (instructor_id, date, start_time, end_time, capacity, location_id, title, price))

            # Your environment/setup needs to ensure data is committed here, if necessary
            return jsonify({'success': True, 'message': 'Lesson added successfully.'})
        except Exception as err:
            # Handle error
            return jsonify({'success': False, 'message': str(err)})
        finally:
            # Always ensure resources are cleaned up
            cursor.close()
    else:
        # User is not logged in
        return jsonify({'success': False, 'message': 'User is not logged in.'}), 401   

## Instuctor's Profile ##
@app.route('/instructor/profile')
def instructor_profile():
    if 'loggedin' in session and session['loggedin']:
        
        encoded_instructor_profile = []

        cursor = utils.getCursor()
        instructorquery = "SELECT * FROM instructor WHERE instructor_id = %s;"
        cursor.execute(instructorquery, (session['id'],))
        instructor = cursor.fetchone()

        if instructor['instructor_image']:
            image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
        else:
            image_encode = None
            
        encoded_instructor_profile.append((
            instructor['instructor_id'], instructor['user_name'], instructor['title'], instructor['first_name'],
            instructor['last_name'], instructor['position'], instructor['phone_number'], instructor['email'],
            instructor['address'], instructor['instructor_profile'], instructor['instructor_image_name'],image_encode
        ))

        return render_template('/instructor/instr_profile.html', account=encoded_instructor_profile, role=session['role'])

    else:
        return redirect(url_for('login'))


## Instructor Edit Profile ##
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

            redirect_route = {
                'Member': 'member_profile',
                'Manager': 'manager_profile',
                'Instructor': 'instructor_profile'
            }.get(session.get('role'), 'login') 

            if len(phone_number) != 10 or not phone_number.isdigit():
                flash('Phone number must be 10 digits', 'danger')
                return redirect(url_for(redirect_route))
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid email address', 'danger')
                return redirect(url_for(redirect_route))
            
            if instructor_image:
                if utils.allowed_file(instructor_image.filename):
                    filename = secure_filename(instructor_image.filename)
                    image_data = instructor_image.read()

                    cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, instructor_profile = %s, instructor_image_name = %s, instructor_image = %s WHERE user_name = %s",
                                    (title, first_name, last_name, position, phone_number, email, address, instructor_profile, filename, image_data, session['username'],))
                    flash('Profile updated successfully with image')
                    return redirect(url_for('instructor_profile')) 
                else:
                    flash('Invalid file type, please upload a valid image file','danger')
                    return redirect(url_for('instructor_profile')) 
            else:

               cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, instructor_profile = %s WHERE user_name = %s",
                            (title, first_name, last_name, position, phone_number, email, address, instructor_profile, session['username'],))
            flash('Profile updated successfully!')
            return redirect(url_for('instructor_profile'))

        else:
            cursor.execute("SELECT * FROM instructor WHERE user_name = %s", (session['username'],))
            instructor = cursor.fetchone()
            return render_template('/instructor/edit_instr_profile.html', instructor=instructor, messages=messages, image_encode=image_encode,role=session['role'])
    else:
        return redirect(url_for('login'))



## Instructor Workshop ##
@app.route('/instructor/workshops')
def instructor_workshops():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        instructor_id = request.args.get('instructor_id')
        date = request.args.get('date')
        location_id = request.args.get('location_id')  # Updated variable name to match column
        
        query = """
        SELECT w.*, i.first_name, i.last_name,locations.name,locations.address 
        FROM workshops w
        JOIN instructor i ON w.instructor_id = i.instructor_id
        JOIN locations ON w.location_id = locations.location_id
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


## Instructor View Workshop Details##
@app.route('/instructor/workshop_details/<int:workshop_id>')
def workshop_details(workshop_id):
    if 'loggedin' not in session or not session['loggedin']:
        return redirect(url_for('login'))

    if session.get('role') != 'Instructor':
        return redirect(url_for('login'))  # Redirect to login if not an instructor

    cursor = utils.getCursor()
    cursor.execute("""
        SELECT w.*, l.name as location_name, i.first_name, i.last_name
        FROM workshops w
        LEFT JOIN locations l ON w.location_id = l.location_id
        LEFT JOIN instructor i ON w.instructor_id = i.instructor_id
        WHERE w.workshop_id = %s
        """, (workshop_id, ))
    workshop = cursor.fetchone()
    cursor.close()

    return render_template('instructor/instr_workshop_details.html', workshop=workshop)

## Instructor View News ##
@app.route('/instr_view_news')
def instr_view_news():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        title = request.args.get('title')
        date = request.args.get('date')
        
        sql_query = """
        SELECT n.news_id, n.title, n.content, n.date_published, 
               m.first_name, m.last_name
        FROM news n
        JOIN manager m ON n.author_id = m.manager_id
        WHERE 1=1
        """
        query_params = []
        
        if title:
            sql_query += " AND n.title LIKE %s"
            query_params.append(f"%{title}%")
        if date:
            sql_query += " AND DATE(n.date_published) = %s"
            query_params.append(date)
        
        sql_query += " ORDER BY n.date_published DESC"
        
        cursor.execute(sql_query, query_params)
        news_articles = cursor.fetchall()
        return render_template('instructor/instr_view_news.html', news_articles=news_articles)
        
    else: 
        return redirect(url_for('instructor/instr_dashboard'))

           
            
## Instructor News - Read More ##
@app.route('/instr_news_details/<int:news_id>')
def instr_news_details(news_id):
    cursor = utils.getCursor()
    
    # Fetch the specific news article by id
    cursor.execute("SELECT title, content, date_published FROM news WHERE news_id = %s", (news_id,))
    article = cursor.fetchone()

    # Check if the article was found
    if article:
        return render_template('instructor/instr_news_details.html', article=article)
    else:
        # If no article found with the provided id, you can redirect to a 404 page or back to the news list
        return "Article not found", 404
    


## Attendance Records - Display all records ##
@app.route('/instructor/attendance')
def attendance_records():
    if 'loggedin' in session and session.get('loggedin'):   
        date_filter = request.args.get('date', None)
        type_filter = request.args.get('type', None)
    
            
        sql = """SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    l.title AS title,
                    l.date AS class_date,
                    l.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN lessons AS l ON b.lesson_id = l.lesson_id
                    JOIN instructor AS i ON l.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\'
                    UNION
                    SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    w.title AS title,
                    w.date AS class_date,
                    w.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN workshops AS w ON b.workshop_id = w.workshop_id
                    JOIN instructor AS i ON w.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\';"""
            
        
            
        cursor = utils.getCursor()
        cursor.execute(sql)    
        records = cursor.fetchall()
            
        return render_template('instructor/instr_attendance.html', records=records)

@app.route('/attendance_search')
def attendance_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute("""SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    l.title AS title,
                    l.date AS class_date,
                    l.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN lessons AS l ON b.lesson_id = l.lesson_id
                    JOIN instructor AS i ON l.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\'
                    UNION
                    SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    w.title AS title,
                    w.date AS class_date,
                    w.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN workshops AS w ON b.workshop_id = w.workshop_id
                    JOIN instructor AS i ON w.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\';""")
        users = cursor.fetchall()
        
        if query is None or query == '':
            return redirect(url_for('attendance_records'))
        
        matched_profiles = []
        for user in users:
            if query.lower() in user['booking_type'].lower():
               cursor.execute(""" SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    l.title AS title,
                    l.date AS class_date,
                    l.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN lessons AS l ON b.lesson_id = l.lesson_id
                    JOIN instructor AS i ON l.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\' AND booking_type LIKE CONCAT('%', %s, '%')
                    UNION
                    SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    w.title AS title,
                    w.date AS class_date,
                    w.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN workshops AS w ON b.workshop_id = w.workshop_id
                    JOIN instructor AS i ON w.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\' AND booking_type LIKE CONCAT('%', %s, '%');""",(user['booking_type'],user['booking_type'],))
               member_profile_list = cursor.fetchall()
               matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['class_date'].strftime('%Y-%m-%d').lower():
                cursor.execute(""" SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    l.title AS title,
                    l.date AS class_date,
                    l.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN lessons AS l ON b.lesson_id = l.lesson_id
                    JOIN instructor AS i ON l.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\' AND l.date LIKE CONCAT('%', %s, '%')
                    UNION
                    SELECT b.booking_id, m.first_name AS member_first_name, m.last_name AS member_last_name,b.booking_type, b.status,
                    w.title AS title,
                    w.date AS class_date,
                    w.start_time AS class_start_time,
                    i.instructor_id, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name
                    FROM bookings AS b
                    JOIN member AS m ON b.user_id = m.member_id
                    JOIN workshops AS w ON b.workshop_id = w.workshop_id
                    JOIN instructor AS i ON w.instructor_id = i.instructor_id 
                    WHERE status = \'Booked\' AND w.date LIKE CONCAT('%', %s, '%');""", (user['class_date'].strftime('%Y-%m-%d'),user['class_date'].strftime('%Y-%m-%d'),))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
        
        if not matched_profiles:
            flash('No matching attendance found.', 'info')
            return redirect(url_for('attendance_records'))
        else:
            return render_template("instructor/instr_attendance.html", records=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))


## Attendance Records - is attended ##
@app.route('/record_attendance', methods=['POST'])
def record_attendance():
    if 'loggedin' in session and session['loggedin']:
        booking_id = request.form.get('booking_id')

        # Update the database to record attendance
        cursor = utils.getCursor()
        cursor.execute(
            'UPDATE bookings SET is_attended = TRUE WHERE booking_id = %s',
            (booking_id,))
        
        utils.connection.commit()
        flash('Member marked as present') 
        # Redirect to the attendance records page or where appropriate
        return redirect(url_for('attendance_records'))
    else:
        # If the user isn't logged in, redirect to the login page
        return redirect(url_for('login'))
    

## Attendance Records - show marked as present ##
@app.route('/attendance_present')
def present_attendance():
    records =[]
    return render_template('/instructor/attendance.html', records=records)

@app.route('/instructor/delete_one_on_one_lesson_instr/<int:lesson_id>')
def delete_one_on_one_lesson_instr(lesson_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM one_on_one_lessons WHERE lesson_id=%s',(lesson_id,))
        
        return redirect(url_for('instructor_lessons'))
    else:
        return redirect(url_for('login'))
    
@app.route('/instructor/delete_group_lesson_instr/<int:lesson_id>')
def delete_group_lesson_instr(lesson_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM lessons WHERE lesson_id=%s',(lesson_id,))
        
        return redirect(url_for('instructor_lessons'))
    else:
        return redirect(url_for('login'))