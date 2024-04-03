from app import app
from flask import render_template,redirect,request,url_for
from flask import session
from flask import flash,get_flashed_messages
from datetime import datetime
from app import utils
from werkzeug.utils import secure_filename
import base64
from flask import jsonify


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
        SELECT ool.*, m.first_name, m.last_name, m.user_name 
        FROM `one_on_one_lessons` ool
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

            if instructor_image:
                if utils.allowed_file(instructor_image.filename):
                    filename = secure_filename(instructor_image.filename)
                    image_data = instructor_image.read()

                    cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, instructor_profile = %s, instructor_image_name = %s, instructor_image = %s WHERE user_name = %s",
                                    (title, first_name, last_name, position, phone_number, email, address, instructor_profile, filename, image_data, session['username'],))
                    flash('Profile updated successfully with image')
                else:
                    flash('Invalid file type, please upload a valid image file')
            else:
                

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



## Instructor Workshop ##
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



## Instructor View News ##
@app.route('/instr_view_news')
def instr_view_news():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        title = request.args.get('title')
        date = request.args.get('date')
        
        sql_query = """
        SELECT n.news_id, n.title, n.content, n.details, n.date_published, 
               m.first_name, m.last_name
        FROM instr_news n
        JOIN manager m ON n.author_id = m.manager_id
        WHERE 1=1
        """
        query_params = []
        
        if title:
            sql_query += " AND title LIKE %s"
            query_params.append(f"%{title}%")
        if date:
            sql_query += " AND DATE(date_published) = %s"
            query_params.append(date)
        
        sql_query += " ORDER BY date_published DESC"
        
        cursor.execute(sql_query, query_params)
        news_articles = cursor.fetchall()
        return render_template('instructor/instr_view_news.html', news_articles=news_articles)
        
    else: 
        return redirect(url_for('instructor/instr_dashboard'))

           
            
## Instructor News - Read More ##
@app.route('/member_news_details/<int:news_id>')
def instr_news_details(news_id):
    cursor = utils.getCursor()
    
    # Fetch the specific news article by id
    cursor.execute("SELECT title, content, date_published, details FROM news WHERE news_id = %s", (news_id,))
    article = cursor.fetchone()

    # Check if the article was found
    if article:
        return render_template('member/member_news_details.html', article=article)
    else:
        # If no article found with the provided id, you can redirect to a 404 page or back to the news list
        return "Article not found", 404
    

