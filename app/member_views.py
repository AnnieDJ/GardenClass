from app import app
from flask import render_template, redirect, url_for,flash
from flask import session,request
from datetime import datetime, timedelta
from app import utils
import re


@app.context_processor
def inject_member_details():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        user_name = session.get('username')

        # Fetch the member details based on the session's username
        cursor.execute("""
        SELECT m.first_name, m.last_name, m.email
        FROM member m
        JOIN user u ON m.member_id = u.related_member_id
        WHERE u.user_name = %s
        """, (user_name,))
        member_info = cursor.fetchone()
        cursor.close()
        
        if member_info:
            full_name = f"{member_info['first_name']} {member_info['last_name']}"
            email = member_info['email']
            return {'member_name': full_name, 'member_email': email}
    return {}


## Member dashboard ##
@app.route('/member/dashboard')
def member_dashboard():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()

        # Fetch upcoming workshops and lessons
        cursor.execute("""
            SELECT w.workshop_id, w.title, w.date, w.start_time, w.end_time, w.price, l.name as location_name, 
            CONCAT(i.first_name, ' ', i.last_name) as instructor_name
            FROM workshops w
            JOIN locations l ON w.location_id = l.location_id
            JOIN instructor i ON w.instructor_id = i.instructor_id
            WHERE w.date >= CURDATE()
            ORDER BY w.date, w.start_time
            LIMIT 1
        """)
        workshops = cursor.fetchall()

        cursor.execute("""
            SELECT les.lesson_id, les.title, les.date, les.start_time, les.end_time, les.price, loc.name as location_name,
            CONCAT(inst.first_name, ' ', inst.last_name) as instructor_name
            FROM lessons les
            JOIN locations loc ON les.location_id = loc.location_id
            JOIN instructor inst ON les.instructor_id = inst.instructor_id
            WHERE les.date >= CURDATE()
            ORDER BY les.date, les.start_time
            LIMIT 1
        """)
        lessons = cursor.fetchall()

        cursor.close()
        
        return render_template('member/member_dashboard.html', workshops=workshops, lessons=lessons)
    else:
        return redirect(url_for('login'))



## Member own profile ##
@app.route('/member/profile')
def member_profile():

    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM member WHERE user_name = %s", (session['username'],))
        
        member_profile = cursor.fetchone()
        
        return render_template('/member/member_profile.html', member_profile = member_profile, role=session['role'])
        
    else:
        return redirect(url_for('login'))
    
    
    
## Member edit own profile ##
@app.route('/member/member_edit_profile', methods=['GET', 'POST'])
def member_edit_profile():
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            address = request.form.get('address')
            date_of_birth = request.form.get('date_of_birth')

                # Redirect user to the appropriate profile page
            redirect_route = {
                'Member': 'member_profile',
                'Manager': 'manager_profile',
                'Instructor': 'instructor_profile'
            }.get(session.get('role'), 'login')  # Fallback to 'login' if role is not found

            # Perform data validation
            if len(phone_number) != 10 or not phone_number.isdigit():
                flash('Phone number must be 10 digits', 'danger')
                return redirect(url_for(redirect_route))
            
            birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
            age = (datetime.now() - birth_date) // timedelta(days=365.25)
            if age < 16:
                flash('You must be at least 16 years old', 'danger')
                return redirect(url_for(redirect_route))
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid email address', 'danger')
                return redirect(url_for(redirect_route))

            cursor.execute("UPDATE member SET title = %s, first_name = %s,  last_name = %s, phone_number = %s, email = %s,address = %s, \
                           date_of_birth = %s WHERE user_name = %s", (title, first_name, last_name,phone_number, email, address,date_of_birth,session['username'],))       
            flash('Profile updated successfully!')
            return redirect(url_for('member_profile'))
        else:
            cursor.execute("SELECT * FROM member WHERE user_name = %s", (session['username'],))
            member_profile = cursor.fetchone()
        
            return render_template('/member/edit_member_profile.html', member_profile = member_profile, role=session['role'])
        
    else:
        return redirect(url_for('login'))




## Member view Instructors list ##
@app.route('/member/member_view_instr')
def member_view_instr():
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute("SELECT instructor_id, title, first_name, last_name, position, phone_number, email, instructor_profile, \
                instructor_image_name FROM instructor")
        member_view_instr = cursor.fetchall()
        
        return render_template('/member/member_view_instr.html', member_view_instr=member_view_instr, role=session.get('role', 'member'))
    else:
        return redirect(url_for('member_dashboard'))



## Member view instructor available lessons ##
@app.route('/member/member_view_1on1')
def member_view_1on1():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()

        # Fetch instructor_id from request when a member clicks on an instructor image
        instructor_id = request.args.get('instructor_id')
        if not instructor_id:
            return "Instructor ID not provided."
        
        try: 
        # Prepare the query for fetching available lessons by the instructor
            ool_query = """SELECT * FROM `one_on_one_lessons` 
                           WHERE instructor_id = %s AND status = 'Scheduled' 
                           ORDER BY date, start_time"""

        # Execute the query
            cursor.execute(ool_query, (instructor_id,))
            one_on_one_lessons_data = cursor.fetchall()
        
        except Exception as e:
            print (f"Database query failed: {e}")
            one_on_one_lessons_data = []
        finally:
            cursor.close()
        
        # Render the template with the fetched data
        return render_template('member/member_view_1on1.html', 
                               one_on_one_lessons_data=one_on_one_lessons_data, 
                               role=session['role'])
    else:
        return redirect(url_for('member_view_instr')) 
    


## Member workshop ##
@app.route('/workshoplist')
def workshoplist():
    connection = utils.getCursor()
    connection.execute("SELECT * FROM workshops;")
    workshopList = connection.fetchall()
    return render_template('/member/member_workshop.html', role=session.get('role', 'member'),workshop_list = workshopList)

@app.route('/workshopimage')
def workshopimage():
    connection = utils.getCursor()
    connection.execute("SELECT * FROM workshops;")
    workshopImage = connection.fetchall()
    return render_template('member_workshop.html', role=session.get('role', 'member'),workshop_image = workshopImage)



    
## Member Search 1-on-1 lessons ##
@app.route('/search_1on1_lessons', methods=['GET', 'POST'])
def search_1on1_lessons():
    if 'loggedin' in session and session['loggedin']:
        msg = request.args.get('msg', None)
        cursor = utils.getCursor()
        
        lesson_name = request.form.get('lesson_name', '') if request.method == 'POST' else ''
        date = request.form.get('date', '') if request.method == 'POST' else ''
        location = request.form.get('location', '') if request.method == 'POST' else ''
        
        query = """SELECT * FROM `one_on_one_lessons` WHERE status = 'Scheduled'"""
        query_params = []
        
        # Add search filters to the query only if they have values
        if lesson_name:
            query += " AND lesson_name LIKE %s"
            query_params.append(f"%{lesson_name}%")
        if date:
            query += " AND date = %s"
            query_params.append(date)
        if location:
            query += " AND location_id LIKE %s"
            query_params.append(f"%{location}%")
        
        query += " ORDER BY date, start_time"

        try: 
            cursor.execute(query, tuple(query_params))
            lessons = cursor.fetchall()
            
            print("Lessons fetched:", lessons)

        except Exception as e:
            print(f"Database query failed: {e}")
            lessons = []
        finally:
            cursor.close()

        # Render the template with the search results
        return render_template('member/member_view_1on1.html', one_on_one_lessons_data=lessons, role=session['role'], msg=msg)
    else:
        return redirect(url_for('member_view_instr')) 



## Member book 1 on1 ##
@app.route('/book_lesson', methods=['POST'])
def book_lesson():
    lesson_id = request.form.get('lesson_id')
    
    if not lesson_id:
        return redirect(url_for('search_1on1_lessons', msg='No lesson selected.'))

    try:
        cursor = utils.getCursor()
        # Fetch the lesson details to display on the booking summary page
        cursor.execute("SELECT * FROM one_on_one_lessons WHERE lesson_id = %s AND status = 'Scheduled'", (lesson_id,))
        booking_details = cursor.fetchone()

        if booking_details:
            return render_template('booking_summary.html', booking=booking_details)
        else:
            return redirect(url_for('search_1on1_lessons', msg='Sorry, this lesson is no longer available or does not exist.'))

    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect(url_for('search_1on1_lessons', msg='An error occurred while retrieving the lesson details.'))

    finally:
        cursor.close()


@app.route('/member_view_news')
def member_view_news():
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
        return render_template('member/member_view_news.html', news_articles=news_articles)
        
    else: 
        return redirect(url_for('login'))  # make sure to redirect to the correct login route



@app.route('/member_news_details/<int:news_id>')
def member_news_details(news_id):
    cursor = utils.getCursor()
    
    # Fetch the specific news article by id
    cursor.execute("SELECT title, content, date_published FROM news WHERE news_id = %s", (news_id,))
    article = cursor.fetchone()

    # Check if the article was found
    if article:
        return render_template('member/member_news_details.html', article=article)
    else:
        # If no article found with the provided id, you can redirect to a 404 page or back to the news list
        return "Article not found", 404
     
@app.route('/member_own_subscription')
def member_own_subscription():
     if 'loggedin' in session and session['loggedin']:
         cursor = utils.getCursor()
         
         cursor.execute('SELECT * FROM subscriptions WHERE user_id = %s AND CURDATE() BETWEEN start_date AND end_date',(session['id'],))
         sub_info = cursor.fetchone()
         
         cursor.execute('SELECT * FROM payments WHERE user_id = %s',(session['id'],))
         payment_history = cursor.fetchall()
         
         return render_template('/member/member_mge_subscription.html',sub_info = sub_info,payment_history = payment_history, role=session['role'])
         
     else: 
         return redirect(url_for('login'))