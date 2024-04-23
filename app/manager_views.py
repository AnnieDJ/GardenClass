from app import app
from flask import render_template,redirect,url_for, g
from flask import session,request,jsonify,flash
from app import utils
from werkzeug.utils import secure_filename
import base64
import re
from datetime import datetime
import mysql.connector
import os
from werkzeug.utils import secure_filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.context_processor
def inject_user_details():
    if 'loggedin' in session and session['loggedin']:
        # Assuming you store username in session['username']
        cursor = utils.getCursor()
        cursor.execute("SELECT first_name, last_name, email FROM manager WHERE user_name = %s", (session['username'],))
        manager_profile = cursor.fetchone()
        cursor.close()
        if manager_profile:
            full_name = f"{manager_profile['first_name']} {manager_profile['last_name']}"
            email = manager_profile['email']
            # Return a dictionary that has the variables you want to inject
            return {'manager_name': full_name, 'email': email}
        return {}
    return {} 

## Manager Dashboard ##
@app.route('/manager/dashboard')
def manager_dashboard():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()

        cursor.execute("SELECT * FROM manager WHERE user_name = %s", (session['username'],))
        manager_profile = cursor.fetchone()

        cursor.execute("SELECT * FROM lessons ORDER BY date, start_time LIMIT 2")
        lesson_data = cursor.fetchall()
        cursor.execute("SELECT * FROM workshops ORDER BY date, start_time LIMIT 2")
        workshop_data = cursor.fetchall()
        cursor.execute("SELECT * FROM news ORDER BY date_published LIMIT 1")
        news_data = cursor.fetchall()
        
        cursor.close()

        if manager_profile:
            return render_template("/manager/mgr_dashboard.html", lessons=lesson_data,
                                   workshops=workshop_data, news=news_data,
                                   username=session['username'], role=session['role'],
                                   manager_name=f"{manager_profile['first_name']} {manager_profile['last_name']}",
                                   email=manager_profile['email'])
        else:
            # Handle case where manager profile is not found
            flash('Manager profile not found', 'error')
            return redirect(url_for('login'))
    
    else:
        return redirect(url_for('login'))


## Manger view own profile ##
@app.route('/manager/profile')
def manager_profile():
    if 'loggedin' in session and session['loggedin']:
        encoded_manager_profile = []

        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM manager WHERE user_name = %s", (session['username'],))
        manager_profile = cursor.fetchone()

        if manager_profile:
            if manager_profile['manager_image_name'] is not None and manager_profile['manager_image_name'] != '' and manager_profile['profile_image']:
                image_encode = base64.b64encode(manager_profile['profile_image']).decode('utf-8')
                encoded_manager_profile.append((manager_profile['manager_id'], manager_profile['user_name'], manager_profile['title'], manager_profile['first_name'], manager_profile['last_name'], manager_profile['position'], manager_profile['phone_number'], manager_profile['email'], manager_profile['manager_image_name'], image_encode, manager_profile['gardering_experience']))
            else:
                encoded_manager_profile.append((manager_profile['manager_id'], manager_profile['user_name'], manager_profile['title'], manager_profile['first_name'], manager_profile['last_name'], manager_profile['position'], manager_profile['phone_number'], manager_profile['email'], manager_profile['manager_image_name'], None, manager_profile['gardering_experience']))

            return render_template('/manager/mgr_profile.html', manager_profile=encoded_manager_profile, role=session['role'])
        else:
            flash('Manager profile not found', 'error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))



## Manager edit own profile ##
@app.route('/manager/editmanagerprofile', methods=['GET', 'POST'])
def editmanagerprofile():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            gardering_experience = request.form.get('gardening_experience')
            manager_image = request.files['manager_image']

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
            
            if manager_image:
                
                if utils.allowed_file(manager_image.filename):
                    filename = secure_filename(manager_image.filename)
                    image_data = manager_image.read()
                    cursor.execute("UPDATE manager SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, gardering_experience = %s, manager_image_name = %s, profile_image = %s  \
                        WHERE user_name = %s", (title, first_name, last_name, position, phone_number, email, gardering_experience, filename,image_data, session['username'],))
                    flash('Profile updated successfully with image')
                    return redirect(url_for('manager_profile'))     
                else:
                    flash('Invalid file type, please upload a valid image file','danger')
                    return redirect(url_for('manager_profile')) 
                    
            else:
                cursor.execute("UPDATE manager SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, gardering_experience = %s \
                   WHERE user_name = %s", (title, first_name, last_name, position, phone_number, email, gardering_experience, session['username'],))

            flash('Profile updated successfully!')
            return redirect(url_for('manager_profile'))
        else:
            cursor.execute("SELECT * FROM manager WHERE user_name = %s", (session['username'],))
            manager_profile = cursor.fetchone()
        
            return render_template('/manager/mgr_profile.html', manager_profile = manager_profile, role=session['role'])
        
    else:
        return redirect(url_for('login'))
    

## Manaer view instructors list ##
@app.route('/manager/instructor_profile_list')
def instructor_profile_list():
    
    if 'loggedin' in session and session['loggedin']: 
        encoded_instructor_profile = []
        
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM instructor;")
        instructor_profile = cursor.fetchall()
        
        for instructor in instructor_profile:
            if instructor['instructor_image_name'] is not None and instructor['instructor_image_name'] != '' and instructor['instructor_image']:
               image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
               encoded_instructor_profile.append((instructor['instructor_id'], instructor['user_name'],instructor['title'] ,instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],image_encode))
            else:
                encoded_instructor_profile.append((instructor['instructor_id'], instructor['user_name'],instructor['title'],instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],None))
            
        return render_template("manager/manage_instr_profile.html", instructor_profile=encoded_instructor_profile, role = session['role'])
    else:
        return redirect(url_for('login'))



## Manager edit/update instructor profile ##
@app.route('/manager/edit_instructor_profile/<int:instructor_id>', methods=['GET', 'POST'])
def edit_instructor_profile(instructor_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            address = request.form.get('address')
            instructor_profile = request.form.get('instructor_profile')
            instructor_image = request.files['instructor_image']
            password = request.form.get('password')
            
            if password is not None and password != '':
               hashed_password = utils.hashing.hash_value(password , salt='schwifty')
               
               if instructor_image: 
                   
                  if utils.allowed_file(instructor_image.filename):
                     filename = secure_filename(instructor_image.filename)
                     image_data = instructor_image.read()
                     cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s,  address = %s, instructor_profile = %s, instructor_image_name = %s, instructor_image = %s WHERE instructor_id = %s",(title,first_name,last_name,position,phone_number,email,address,instructor_profile,filename,image_data,instructor_id,))
                     cursor.execute("UPDATE user SET password = %s WHERE related_instructor_id = %s",(hashed_password,instructor_id,))
                  else:
                      flash("This is not a valid Image!")
                      return redirect(url_for('instructor_profile_list'))
                   
               else:
                   cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s,  address = %s, instructor_profile = %s WHERE instructor_id = %s",(title,first_name,last_name,position,phone_number,email,address,instructor_profile,instructor_id,))
                   cursor.execute("UPDATE user SET password = %s WHERE related_instructor_id = %s",(hashed_password,instructor_id,))
            else:
                if instructor_image:
                   
                   if utils.allowed_file(instructor_image.filename):
                   
                      filename = secure_filename(instructor_image.filename)
                      image_data = instructor_image.read()
                      cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s,  address = %s, instructor_profile = %s, instructor_image_name = %s, instructor_image = %s WHERE instructor_id = %s",(title,first_name,last_name,position,phone_number,email,address,instructor_profile,filename,image_data,instructor_id,))
                   else:
                       flash("This is not a valid Image!")
                       return redirect(url_for('instructor_profile_list',))
                else:
                   cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s,  address = %s, instructor_profile = %s WHERE instructor_id = %s",(title,first_name,last_name,position,phone_number,email,address,instructor_profile,instructor_id,))
             
            return redirect(url_for('instructor_profile_list'))
            
        else:
            cursor.execute("SELECT * FROM instructor WHERE instructor_id = %s;",(instructor_id,))      
            instructor = cursor.fetchone()
            return render_template("/manager/edit_instr_profile.html", instructor=instructor, role = session['role'])
        
       
    else:
        return redirect(url_for('login'))
    
    
  
## Manager delete instructor profile ##    
@app.route('/manager/delete_instructor_profile/<int:instructor_id>')
def delete_instructor_profile(instructor_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM instructor WHERE instructor_id=%s',(instructor_id,))
        cursor.execute('DELETE FROM user WHERE related_instructor_id=%s',(instructor_id,))
        
        return redirect(url_for('instructor_profile_list'))
    else:
        return redirect(url_for('login'))


## Manager view members list ##
@app.route('/manager/member_profile_list')
def member_profile_list():
    
    if 'loggedin' in session and session['loggedin']: 
        
        cursor = utils.getCursor()
        cursor.execute("""SELECT member_id,user_name,title,first_name,last_name,position,phone_number,email,address,date_of_birth,
                          subscriptions.start_date AS subscription_date,subscriptions.type,subscriptions.end_date AS expiry_date
                          FROM member 
                          JOIN subscriptions ON member.member_id = subscriptions.user_id;""")
        member_profile = cursor.fetchall()
        
            
        return render_template("manager/manage_member_profile.html", member_profile=member_profile, role = session['role'])
    else:
        return redirect(url_for('login'))
 
 
## Manager edit/update member profile ##   
@app.route('/manager/edit_member_profile/<int:member_id>', methods=['GET', 'POST'])
def edit_member_profile(member_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            address = request.form.get('address')
            date_of_birth = request.form.get('date_of_birth')
            subscription_date = request.form.get('subscription_date')
            type = request.form.get('type')
            expiry_date = request.form.get('expiry_date')
            password = request.form.get('password')
            
            if password is not None and password != '':
               hashed_password = utils.hashing.hash_value(password , salt='schwifty')
               cursor.execute("UPDATE member SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, date_of_birth = %s, subscription_date = %s, type = %s, expiry_date = %s WHERE member_id = %s",(title,first_name,last_name,position,phone_number,email,address,date_of_birth,subscription_date, type,expiry_date,member_id,))
               cursor.execute("UPDATE user SET password = %s WHERE related_member_id = %s",(hashed_password,member_id,))
               cursor.execute("UPDATE subscriptions SET start_date = %s,end_date = %s, type = %s WHERE user_id = %s",(subscription_date,expiry_date,type,member_id,))
                   
            else: 
               cursor.execute("UPDATE member SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, date_of_birth = %s, subscription_date = %s, type = %s, expiry_date = %s WHERE member_id = %s",(title,first_name,last_name,position,phone_number,email,address,date_of_birth,subscription_date, type,expiry_date,member_id,))
               cursor.execute("UPDATE subscriptions SET start_date = %s,end_date = %s, type = %s WHERE user_id = %s",(subscription_date,expiry_date,type,member_id,))
             
            return redirect(url_for('member_profile_list'))
            
        else:
            cursor.execute('SELECT member_id,user_name,title,first_name,last_name,position,phone_number,email,address,date_of_birth,\
                            subscriptions.start_date AS subscription_date,subscriptions.type,subscriptions.end_date AS expiry_date\
                            FROM member \
                            JOIN subscriptions ON member.member_id = subscriptions.user_id; WHERE member_id = %s;',(member_id,))      
            member = cursor.fetchone()
            return render_template("/manager/edit_member_profile.html", member=member, role = session['role'])
        
       
    else:
        return redirect(url_for('login'))
    
    
    
## Manager delete member profile ##    
@app.route('/manager/delete_member_profile/<int:member_id>')
def delete_member_profile(member_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM member WHERE member_id=%s',(member_id,))
        cursor.execute('DELETE FROM user WHERE related_member_id=%s',(member_id,))
        
        return redirect(url_for('member_profile_list'))
    else:
        return redirect(url_for('login'))

#For checking email is unique and has to be unique  
@app.route('/check_email', methods=['POST'])
def check_email():
    if 'loggedin' in session and session['loggedin']:
        email = request.form['email']
    
        cursor = utils.getCursor()   
        cursor.execute('SELECT email FROM instructor;')
        email_list = cursor.fetchall()

        if email_list:  
           if any(email == row['email'] for row in email_list):
               
              return jsonify({'valid': False})
           else:
              return jsonify({'valid': True})
        else:
          return jsonify({'valid': True})  

    
@app.route('/instr_search')
def instr_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
        results = []
      
        cursor = utils.getCursor()
        cursor.execute('SELECT user_name, email, address, position FROM instructor;')
        users = cursor.fetchall()
        
        if query is None or query == '':
            return redirect(url_for('instructor_profile_list'))
        
        for user in users:
            if query.lower() in user['user_name'].lower():
               cursor.execute("SELECT * FROM instructor WHERE user_name LIKE CONCAT('%', %s, '%');",(user['user_name'],))
               instructor_profile_list = cursor.fetchall()
             
               for instructor in instructor_profile_list:
                   if instructor['instructor_image_name'] is not None and instructor['instructor_image_name'] != '':
                      image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'] ,instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],image_encode))
                   else:
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'],instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],None))
            
               return render_template("manager/manage_instr_profile.html", instructor_profile=results, role = session['role'])
           
            elif query.lower() in user['email'].lower():
               cursor.execute("SELECT * FROM instructor WHERE email LIKE CONCAT('%', %s, '%');",(user['email'],))
               instructor_profile_list = cursor.fetchall()
              
               for instructor in instructor_profile_list:
                   if instructor['instructor_image_name'] is not None and instructor['instructor_image_name'] != '':
                      image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'] ,instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],image_encode))
                   else:
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'],instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],None))
            
               return render_template("manager/manage_instr_profile.html", instructor_profile=results, role = session['role'])
           
            elif query.lower() in user['address'].lower():
                cursor.execute("SELECT * FROM instructor WHERE address LIKE CONCAT('%', %s, '%');",(user['address'],))
                instructor_profile_list = cursor.fetchall()
                
                for instructor in instructor_profile_list:
                   if instructor['instructor_image_name'] is not None and instructor['instructor_image_name'] != '':
                      image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'] ,instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],image_encode))
                   else:
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'],instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],None))
            
                return render_template("manager/manage_instr_profile.html", instructor_profile=results, role = session['role'])
            
            elif query.lower() in user['position'].lower():
                cursor.execute("SELECT * FROM instructor WHERE position LIKE CONCAT('%', %s, '%');",(user['position'],))
                instructor_profile_list = cursor.fetchall()
                
                for instructor in instructor_profile_list:
                   if instructor['instructor_image_name'] is not None and instructor['instructor_image_name'] != '':
                      image_encode = base64.b64encode(instructor['instructor_image']).decode('utf-8')
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'] ,instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],image_encode))
                   else:
                      results.append((instructor['instructor_id'], instructor['user_name'],instructor['title'],instructor['first_name'], instructor['last_name'], instructor['position'],instructor['phone_number'],instructor['email'],instructor['address'],instructor['instructor_profile'],instructor['instructor_image_name'],None))
            
                return render_template("manager/manage_instr_profile.html", instructor_profile=results, role = session['role'])
            
        flash('User does not exist.')
        return redirect(url_for('instructor_profile_list'))
    else:
         return redirect(url_for('login'))

@app.route('/member_search')
def member_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute('SELECT user_name, email, address, position FROM member;')
        users = cursor.fetchall()
        
        if query is None or query == '':
            return redirect(url_for('member_profile_list'))
        
        matched_profiles = []
        for user in users:
            if query.lower() in user['user_name'].lower():
               cursor.execute("SELECT * FROM member WHERE user_name LIKE CONCAT('%', %s, '%');",(user['user_name'],))
               member_profile_list = cursor.fetchall()
               matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['email'].lower():
               cursor.execute("SELECT * FROM member WHERE email LIKE CONCAT('%', %s, '%');",(user['email'],))
               member_profile_list = cursor.fetchall()
               matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['address'].lower():
                cursor.execute("SELECT * FROM member WHERE address LIKE CONCAT('%', %s, '%');",(user['address'],))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['position'].lower():
                cursor.execute("SELECT * FROM member WHERE position LIKE CONCAT('%', %s, '%');",(user['position'],))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
        
        if not matched_profiles:
            flash('No matching users found.', 'info')
            return redirect(url_for('member_profile_list'))
        else:
            return render_template("manager/manage_member_profile.html", member_profile=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))


@app.route('/add/locations', methods=['GET'])
def add_locations_details():
    cursor = utils.getCursor()

    # Fetch locations
    cursor.execute("SELECT location_id, name FROM locations")
    locations = cursor.fetchall()

    # Fetch instructors
    cursor.execute("SELECT instructor_id, first_name, last_name FROM instructor")
    instructors = cursor.fetchall()

    # Fetch members
    cursor.execute("SELECT member_id, first_name, last_name FROM member")
    members = cursor.fetchall()

    cursor.close()

    # Prepare data for JSON response
    locations_list = [{'id': loc['location_id'], 'name': loc['name']} for loc in locations]
    instructors_list = [{'id': instr['instructor_id'], 'name': f"{instr['first_name']} {instr['last_name']}"} for instr in instructors]
    members_list = [{'id': memb['member_id'], 'name': f"{memb['first_name']} {memb['last_name']}"} for memb in members]

    # Combine all data into one dictionary
    combined_data = {
        'locations': locations_list,
        'instructors': instructors_list,
        'members': members_list
    }

    return jsonify(combined_data)




@app.route('/manager/mgr_lessons')
def manager_lessons():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()

        # Fetch parameters from request
        instructor_id = request.args.get('instructor_id')
        member_id = request.args.get('member_id')
        date = request.args.get('date')
        location_id = request.args.get('location_id')

        # Initialize params list for the queries
        ool_params = []
        lessons_params = []

        # Common filters applicable to both queries, with their parameters
        ool_where_clauses = []
        lessons_where_clauses = []

        # Add common filters with table alias to avoid ambiguity
        if instructor_id:
            ool_where_clauses.append("o.instructor_id = %s")
            lessons_where_clauses.append("l.instructor_id = %s")
            ool_params.append(instructor_id)
            lessons_params.append(instructor_id)
        if date:
            ool_where_clauses.append("o.date = %s")
            lessons_where_clauses.append("l.date = %s")
            ool_params.append(date)
            lessons_params.append(date)
        if location_id:
            ool_where_clauses.append("o.location_id = %s")
            lessons_where_clauses.append("l.location_id = %s")
            ool_params.append(location_id)
            lessons_params.append(location_id)

        # Add One-on-One Lessons specific filters
        if member_id:
            ool_where_clauses.append("o.member_id = %s")
            ool_params.append(member_id)

        # Construct WHERE clause for One-on-One Lessons query with JOIN to get member details
        ool_where_clause = " AND ".join(ool_where_clauses) if ool_where_clauses else "1=1"
        ool_query = f"""SELECT o.*, m.user_name, m.first_name, m.last_name FROM `one_on_one_lessons` o 
                        JOIN member m ON o.member_id = m.member_id
                        WHERE {ool_where_clause} 
                        ORDER BY o.date, o.start_time"""

        # Execute query for One-on-One Lessons
        cursor.execute(ool_query, ool_params)
        one_on_one_lessons_data = cursor.fetchall()

        # Construct WHERE clause for Lessons query with JOIN to get instructor details
        lessons_where_clause = " AND ".join(lessons_where_clauses) if lessons_where_clauses else "1=1"
        lessons_query = f"""SELECT l.*, i.user_name, i.first_name, i.last_name FROM `lessons` l 
                            JOIN instructor i ON l.instructor_id = i.instructor_id
                            WHERE {lessons_where_clause} 
                            ORDER BY l.date, l.start_time"""

        # Execute query for Lessons
        cursor.execute(lessons_query, lessons_params)
        group_lessons_data = cursor.fetchall()

        cursor.close()

        return render_template('manager/mgr_lessons.html',
                               one_on_one_lessons_data=one_on_one_lessons_data,
                               group_lessons_data=group_lessons_data,
                               role=session['role'])
    else:
        return redirect(url_for('login'))
    
@app.route('/update_lesson', methods=['POST'])
def update_lesson():
    if 'loggedin' in session:
        source_page = request.form.get('sourcePage') 
        if source_page == 'mgr_lessons':
            lesson_id = request.form.get('lessonID')
            date = request.form.get('date')
            start_time = request.form.get('startTime')
            end_time = request.form.get('endTime')

        
            start_time_obj = datetime.strptime(start_time, "%H:%M" if len(start_time) <= 5 else "%H:%M:%S")
            end_time_obj = datetime.strptime(end_time, "%H:%M" if len(end_time) <= 5 else "%H:%M:%S")
        
            start_time_formatted = start_time_obj.strftime("%H:%M:%S")
            end_time_formatted = end_time_obj.strftime("%H:%M:%S")
            location_id = request.form.get('locationID')
            status = request.form.get('status')
            price = request.form.get('price') 
    
            cursor = utils.getCursor()

        
            update_query = """
            UPDATE one_on_one_lessons
            SET date = %s, start_time = %s, end_time = %s, location_id = %s, status = %s, price = %s
            WHERE lesson_id = %s
            """
            update_values = (date, start_time_formatted, end_time_formatted, location_id, status, price, lesson_id)

            try:
            
                cursor.execute(update_query, update_values)

            
                if cursor.rowcount > 0:
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'message': 'Failed to find the corresponding course information or update failed.'})
            except Exception as e:
                
                print(f"An error occurred: {e}")
                return jsonify({'success': False, 'message': 'Database update error.'})


        else:
            lesson_id = request.form.get('lessonID')
            date = request.form.get('Date')
            start_time = request.form.get('StartTime')
            end_time = request.form.get('EndTime')

        
            start_time_obj = datetime.strptime(start_time, "%H:%M" if len(start_time) <= 5 else "%H:%M:%S")
            end_time_obj = datetime.strptime(end_time, "%H:%M" if len(end_time) <= 5 else "%H:%M:%S")
        
            start_time_formatted = start_time_obj.strftime("%H:%M:%S")
            end_time_formatted = end_time_obj.strftime("%H:%M:%S")
            location_id = request.form.get('LocationID')
            status = request.form.get('Status')
            price = request.form.get('Price') 
        

        
            cursor = utils.getCursor()

        
            update_query = """
            UPDATE one_on_one_lessons
            SET date = %s, start_time = %s, end_time = %s, location_id = %s, status = %s, price = %s
            WHERE lesson_id = %s
            """
            update_values = (date, start_time_formatted, end_time_formatted, location_id, status, price, lesson_id)

            try:
            
                cursor.execute(update_query, update_values)

            
                if cursor.rowcount > 0:
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'message': 'Failed to find the corresponding course information or update failed.'})
            except Exception as e:
                
                print(f"An error occurred: {e}")
                return jsonify({'success': False, 'message': 'Database update error.'})

@app.route('/api/locations', methods=['GET'])
def get_locations():
    try:
        cursor = utils.getCursor()
        cursor.execute("SELECT location_id, name FROM locations")
        locations = cursor.fetchall()
        locations_list = [{'id': loc['location_id'], 'name': loc['name']} for loc in locations]
        return jsonify(locations_list)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Could not fetch locations"}), 500
    
@app.route('/edit', methods=['GET', "POST"])
def edit():
    nid = request.args.get('nid', type=int)

    
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        if request.method == "GET":
           
            cursor.execute("SELECT * FROM one_on_one_lessons WHERE id = %s", (nid,))
            info = cursor.fetchone()  
            if info:
                return render_template('edit_mgr_one_on_one_lessons.html', info=info)
            else:
                return "Record not found", 404

        
        name = request.form.get('name')
        age = request.form.get('age')

       
        update_query = "UPDATE one_on_one_lessons SET name = %s, age = %s WHERE id = %s"
        cursor.execute(update_query, (name, age, nid))
        cursor.connection.commit()  

        cursor.close()
        return redirect(url_for('manager_lessons'))  
    else:
        return redirect(url_for('login'))


@app.route('/add_lesson', methods=['POST'])
def add_lesson():
    if 'loggedin' in session:
        instructor_id = request.form.get('instructor_id')
        member_id = request.form.get('member_id')  
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        price = request.form.get('price')
        status = request.form.get('status')
        capacity = request.form.get('capacity', type=int)
        location_id = request.form.get('location_id')
        title = request.form.get('title')
        lesson_type = request.form.get('lesson_type')
        
        date_f = datetime.strptime(date, '%Y-%m-%d')

        cursor = utils.getCursor()

        try:
            
            cursor.execute("""
                SELECT * FROM one_on_one_lessons
                WHERE instructor_id = %s AND member_id = %s AND date = %s AND start_time = %s AND end_time = %s AND price = %s AND status = %s AND location_id = %s 
            """, (instructor_id, member_id, date, start_time, end_time, price, status, location_id))
            one_on_one_exists = cursor.fetchone()

            cursor.execute("""
                SELECT * FROM lessons
                WHERE instructor_id = %s AND date = %s AND start_time = %s AND end_time = %s AND capacity = %s AND location_id = %s AND title = %s AND price = %s
            """, (instructor_id, date, start_time, end_time, capacity, location_id, title, price))
            lesson_exists = cursor.fetchone()

            if one_on_one_exists or lesson_exists:
                return jsonify({'success': False, 'message': 'A lesson with the same details already exists. Please enter different details.'})

            
            if lesson_type == 'group':
                cursor.execute("SELECT capacity FROM locations WHERE location_id = %s", (location_id,))
                location_capacity_result = cursor.fetchone()
                if location_capacity_result:
                    location_max_capacity = location_capacity_result['capacity']
                    if not (0 < capacity <= location_max_capacity):
                       
                        return jsonify({
                            'success': False,
                            'message': f'Invalid capacity. Capacity must be greater than 0 and cannot exceed {location_max_capacity}.'
                        })
            
                    elif start_time >= end_time:
                          return jsonify({'success': False,'message': 'Start time must be earlier than end time.'})
                    elif date_f < utils.current_date_time():
                          return jsonify({'success': False,'message': 'Date must be later than current date.'})
                    elif int(capacity) <0 or float(price) < 0.0:
                         return jsonify({'success': False,'message': 'Price and capacity must be greater than or equal to 0.'})
            
                    else:
       
                        cursor.execute("""
                                INSERT INTO lessons (instructor_id, date, start_time, end_time, capacity, location_id, title, price)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                 """, (instructor_id, date, start_time, end_time, capacity, location_id, title, price))
                else:
                    
                        return jsonify({
                            'success': False,
                            'message': 'Location not found or does not have a capacity set.'
                        })

            elif lesson_type == 'one_on_one':
                
                    if start_time >= end_time:
                          return jsonify({'success': False,'message': 'Start time must be earlier than end time.'})
                    elif date_f < utils.current_date_time():
                          return jsonify({'success': False,'message': 'Date must be later than current date.'})
                    elif float(price) < 0.0:
                         return jsonify({'success': False,'message': 'Price must be greater than or equal to 0.'})
                    else:
                     
                         cursor.execute("""
                                 INSERT INTO one_on_one_lessons (instructor_id, member_id, date, start_time, end_time, price, status, location_id)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                 """, (instructor_id, member_id, date, start_time, end_time, price, status, location_id))

            else:
                return jsonify({'success': False, 'message': 'Invalid lesson type specified.'})

            # Commit the transaction
            return jsonify({'success': True, 'message': 'Lesson added successfully.'})
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': str(err)})
        finally:
            cursor.close()  # Close the cursor to clean up resources
    else:
        return jsonify({'success': False, 'message': 'User is not logged in.'}), 401


# Route to display the edit form
@app.route('/refresh_lesson', methods=['POST'])
def refresh_lesson():
    if 'loggedin' in session:
        if request.form.get('sourcePage') == "fromInstrutorLesson":
            lesson_id = request.form.get('lessonID')
            date = request.form.get('date')
            start_time = request.form.get('startTime')
            end_time = request.form.get('endTime')

        
            start_time_obj = datetime.strptime(start_time, "%H:%M" if len(start_time) <= 5 else "%H:%M:%S")
            end_time_obj = datetime.strptime(end_time, "%H:%M" if len(end_time) <= 5 else "%H:%M:%S")
            title = request.form.get('title') 
            start_time_formatted = start_time_obj.strftime("%H:%M:%S")
            end_time_formatted = end_time_obj.strftime("%H:%M:%S")
            location_id = request.form.get('locationID')
            capacity=request.form.get('capacity')
            price = request.form.get('price') 
 
            date_f = datetime.strptime(date, '%Y-%m-%d')
      
            cursor = utils.getCursor()       
            
            cursor.execute('SELECT * FROM locations WHERE location_id = %s',(location_id,))
            location_capacity = cursor.fetchone()
            
            if start_time >= end_time:
                     return jsonify({'success': False,'message': 'Start time must be earlier than end time.'})
            elif date_f < utils.current_date_time():
                     return jsonify({'success': False,'message': 'Date must be later than current date.'})
            elif int(capacity) <0 or float(price) < 0.0:
                     return jsonify({'success': False,'message': 'Price and capacity must be greater than or equal to 0.'})
            elif int(capacity) > location_capacity['capacity']:
                     return jsonify({'success': False,'message': 'Capacity must be less than or equal to location capacity.'})
            else:

        
                 update_query = """
                        UPDATE lessons
                        SET date = %s, start_time = %s, end_time = %s, location_id = %s, capacity = %s, price = %s
                        WHERE lesson_id = %s
                      """
                 update_values = (date, start_time_formatted, end_time_formatted, location_id, capacity, price, lesson_id)

                 try:
            
                      cursor.execute(update_query, update_values)

                      if cursor.rowcount > 0:
                          return jsonify({'success': True})
                      else:
                          return jsonify({'success': False, 'message': 'Failed to find the corresponding course information or update failed.'})
                 except Exception as e:
                
                      return jsonify({'success': False, 'message': 'Database update error:{e}.'})
                 finally:
            
                      cursor.close()
        else:
            lesson_id = request.form.get('lessonID')
            date = request.form.get('date')
            start_time = request.form.get('startTime')
            end_time = request.form.get('endTime')

        
            start_time_obj = datetime.strptime(start_time, "%H:%M" if len(start_time) <= 5 else "%H:%M:%S")
            end_time_obj = datetime.strptime(end_time, "%H:%M" if len(end_time) <= 5 else "%H:%M:%S")
            title = request.form.get('title') 
            start_time_formatted = start_time_obj.strftime("%H:%M:%S")
            end_time_formatted = end_time_obj.strftime("%H:%M:%S")
            location_id = request.form.get('locationID')
            capacity=request.form.get('capacity')
            price = request.form.get('price') 
     
            date_f = datetime.strptime(date, '%Y-%m-%d')
      
            cursor = utils.getCursor()       
            
            cursor.execute('SELECT * FROM locations WHERE location_id = %s',(location_id,))
            location_capacity = cursor.fetchone()
            
            if start_time >= end_time:
                     return jsonify({'success': False,'message': 'Start time must be earlier than end time.'})
            elif date_f < utils.current_date_time():
                     return jsonify({'success': False,'message': 'Date must be later than current date.'})
            elif int(capacity) <0 or float(price) < 0.0:
                     return jsonify({'success': False,'message': 'Price and capacity must be greater than or equal to 0.'})
            elif int(capacity) > location_capacity['capacity']:
                     return jsonify({'success': False,'message': 'Capacity must be less than or equal to location capacity.'})
            else:

        
                update_query = """
                       UPDATE lessons
                       SET date = %s, start_time = %s, end_time = %s, location_id = %s, capacity = %s, price = %s
                       WHERE lesson_id = %s
                    """
                update_values = (date, start_time_formatted, end_time_formatted, location_id, capacity, price, lesson_id)

                try:
            
                      cursor.execute(update_query, update_values)

            
                      if cursor.rowcount > 0:
                             return jsonify({'success': True})
                      else:
                             return jsonify({'success': False, 'message': 'Failed to find the corresponding course information or update failed.'})
                except Exception as e:
                
                      return jsonify({'success': False, 'message': 'Database update error:{e}.'})
                finally:
            
                      cursor.close()

          #  return redirect(url_for('login'))



@app.route('/edit_group_lessons', methods=['GET', "POST"])
def edit_lessons():
    nid = request.args.get('nid', type=int)

    
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        if request.method == "GET":
           
            cursor.execute("SELECT * FROM lessons WHERE id = %s", (nid,))
            info = cursor.fetchone()  
            if info:
                return render_template('edit_mgr_lessons.html', info=info)
            else:
                return "Record not found", 404

        
        name = request.form.get('name')
        age = request.form.get('age')

       
        update_query = "UPDATE lessons SET name = %s, age = %s WHERE id = %s"
        cursor.execute(update_query, (name, age, nid))
        cursor.connection.commit()  

        cursor.close()
        return redirect(url_for('manager_lessons'))  
    else:
        return redirect(url_for('login'))


@app.route('/delete_one_on_one_lesson/<int:lesson_id>', methods=['POST'])
def delete_one_on_one_lesson(lesson_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'You must be logged in to perform this action.'}), 401
    try:
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM one_on_one_lessons WHERE lesson_id = %s", (lesson_id,))
        memeber = cursor.fetchall()[0]['member_id']
        
        title = "Your one on one lesson has been cancelled"
        content = "Your one on one lesson has been cancelled becasue manager has deleted it."
        date = utils.current_date_time()
        
    
        cursor.execute("DELETE FROM one_on_one_lessons WHERE lesson_id = %s", (lesson_id,))
        cursor.execute("INSERT INTO news(title,content,date_published,user_id,author_id) VALUES(%s,%s,%s,%s,%s)",(title,content,date,memeber,session['id'],))
       
        return jsonify({'success': True, 'message': 'One-on-one lesson deleted successfully.'})
    except Exception as e:
        
        return jsonify({'success': False, 'message': f'Failed to delete one-on-one lesson. Error: {e}'})


@app.route('/delete_group_lesson/<int:lesson_id>', methods=['POST'])
def delete_group_lesson(lesson_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'You must be logged in to perform this action.'}), 401
    try:
            cursor = utils.getCursor()
            cursor.execute("SELECT title FROM lessons WHERE lesson_id = %s", (lesson_id,))
            lessons_title = cursor.fetchall()[0]['title']
        
            title = f"Lesson %s has been cancelled" %lessons_title 
            content = f"Lesson %s has been cancelled becasue manager has deleted it." %lessons_title
            date = utils.current_date_time()
            
            # Execute the SQL command to delete the lesson
            cursor.execute("DELETE FROM lessons WHERE lesson_id = %s", (lesson_id,))
            cursor.execute("INSERT INTO news(title,content,date_published,author_id) VALUES(%s,%s,%s,%s)",(title,content,date,session['id'],))
            
            return jsonify({'success': True, 'message': 'group lesson deleted successfully.'})
    except Exception as e:
        
        return jsonify({'success': False, 'message': f'Failed to delete group lesson. Error: {e}'})


@app.route('/manager/workshops')
def manager_workshops():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        instructor_id = request.args.get('instructor_id')
        date = request.args.get('date')
        location_id = request.args.get('location_id')  # Assuming the correct parameter is location_id
        
        params = []
        conditions = []
        query = """
        SELECT w.*, i.first_name, i.last_name,locations.name,locations.address
        FROM workshops w
        JOIN instructor i ON w.instructor_id = i.instructor_id
        JOIN locations ON w.location_id = locations.location_id
        """

        if instructor_id:
            conditions.append("w.instructor_id = %s")
            params.append(instructor_id)
        if date:
            conditions.append("w.date = %s")
            params.append(date)
        if location_id:  # Ensure you are using location_id or the correct column name
            conditions.append("w.location_id = %s")  # Corrected column name if it's location_id
            params.append(location_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY w.date"
        
        cursor.execute(query, params)  # Using parameters to safely execute the query
        workshops_data = cursor.fetchall()
        
        return render_template('manager/mgr_workshops.html', workshops=workshops_data, role=session['role'])
    else:
        return redirect(url_for('login'))

@app.route('/update_workshop', methods=['POST'])
def update_workshops():
    if 'loggedin' in session:
        # Extract data from form submission
        workshop_id = request.form.get('workshop_id')
        
        location_id = request.form.get('location_id')
        
        title = request.form.get('title')
        price = request.form.get('price')
        capacity = request.form.get('capacity')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
		
        start_time_obj = datetime.strptime(start_time, "%H:%M" if len(start_time) <= 5 else "%H:%M:%S")
        end_time_obj = datetime.strptime(end_time, "%H:%M" if len(end_time) <= 5 else "%H:%M:%S")
      
        start_time_formatted = start_time_obj.strftime("%H:%M:%S")
        end_time_formatted = end_time_obj.strftime("%H:%M:%S")
        
        cursor = utils.getCursor()
        
        date_f = datetime.strptime(date, '%Y-%m-%d')
            
        cursor.execute('SELECT * FROM locations WHERE location_id = %s',(location_id,))
        location_capacity = cursor.fetchone()
            
        if start_time >= end_time:
            return jsonify({'success': False,'message': 'Start time must be earlier than end time.'})
        elif date_f < utils.current_date_time():
            return jsonify({'success': False,'message': 'Date must be later than current date.'})
        elif int(capacity) <0 or float(price) < 0.0:
            return jsonify({'success': False,'message': 'Price and capacity must be greater than or equal to 0.'})
        elif int(capacity) > location_capacity['capacity']:
            return jsonify({'success': False,'message': 'Capacity must be less than or equal to location capacity.'})
        else:

            update_query = """
                    UPDATE workshops
                    SET date = %s, start_time = %s, end_time = %s, location_id = %s, capacity = %s, price = %s, title = %s
                    WHERE workshop_id = %s
                    """
            update_values = (date, start_time_formatted, end_time_formatted, location_id, capacity, price, title, workshop_id)

            try:
                cursor.execute(update_query, update_values)

           
                if cursor.rowcount > 0:
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'message': 'Failed to find the corresponding course information or update failed.'})
            except Exception as e:
            
                 return jsonify({'success': False, 'message': 'Database update error:{e}.'})

    else:
        return redirect(url_for('login'))

@app.route('/api/instructors', methods=['GET'])
def get_instructors():
    cursor = utils.getCursor()
    cursor.execute("SELECT instructor_id, first_name, last_name FROM instructor")  
    instructors = cursor.fetchall()
    cursor.close()
    
    instructors_list = [
        {'id': ins['instructor_id'], 'name': f"{ins['first_name']} {ins['last_name']}"}
        for ins in instructors
    ]
    return jsonify(instructors_list)
    
@app.route('/api/workshopslocations', methods=['GET'])
def get_workshopslocations():
    cursor = utils.getCursor()  
    cursor.execute("SELECT location_id, name FROM locations")  
    locations = cursor.fetchall()
    cursor.close()

  
    locations_list = [{'id': loc['location_id'], 'name': loc['name']} for loc in locations]
    
    return jsonify(locations_list)



@app.route('/manager/delete_workshop/<int:workshop_id>', methods=['POST'])
def delete_workshop(workshop_id):
    if 'loggedin' in session and session['role'] == 'Manager':
        
        cursor = utils.getCursor()
             
        cursor.execute("SELECT title FROM workshops WHERE workshop_id = %s", (workshop_id,))
        workshop_title = cursor.fetchall()[0]['title']
        
        title = f"workshop %s has been cancelled" %workshop_title 
        content = f"workshop %s has been cancelled becasue manager has deleted it." %workshop_title
        date = utils.current_date_time()
        
        cursor.execute("DELETE FROM workshops WHERE workshop_id = %s", (workshop_id,))
        cursor.execute("INSERT INTO news(title,content,date_published,author_id) VALUES(%s,%s,%s,%s)",(title,content,date,session['id'],))
        return redirect(url_for('manager_workshops'))
    else:
        return redirect(url_for('login'))
    
# @app.route('/manager/add_workshop', methods=['POST'])
# def add_workshop():
#     if 'loggedin' in session and session['role'] == 'Manager':
#         try:
            
#             title = request.form.get('title')
#             instructor_id = request.form.get('instructor_id')
#             location_id = request.form.get('location_id')
#             price = request.form.get('price')
#             capacity = request.form.get('capacity')
#             date = request.form.get('addDate')
#             start_time = request.form.get('starttime')
#             end_time = request.form.get('endtime')
#             workshop_image = 'workshops_images/workshop1.png'  

#             cursor = utils.getCursor()

           
#             sql = "INSERT INTO workshops (title, instructor_id, location_id, price, capacity, date, start_time, end_time, workshop_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
#             val = (title, instructor_id, location_id, price, capacity, date, start_time, end_time, workshop_image)

           
#             cursor.execute(sql, val)
         

#             return jsonify({'success': True, 'message': 'Workshop added successfully.'})
#         except Exception as e:
#             return jsonify({'success': False, 'message': str(e)})
#     else:
#         return jsonify({'success': False, 'message': 'Unauthorized access.'})


import os

@app.route('/manager/add_workshop', methods=['POST'])
def add_workshop():
    if 'loggedin' in session and session['role'] == 'Manager':
        try:
            cursor = utils.getCursor()
            title = request.form['title']
            instructor_id = request.form['instructor_id']
            location_id = request.form['location_id']
            price = request.form['price']
            capacity = request.form['capacity']
            date = request.form['addDate']
            start_time = request.form['starttime']
            end_time = request.form['endtime']
            
            date_f = datetime.strptime(date, '%Y-%m-%d')
            
            cursor.execute('SELECT * FROM locations WHERE location_id = %s',(location_id,))
            location_capacity = cursor.fetchone()
            
            if start_time >= end_time:
                return jsonify({'success': False,'message': 'Start time must be earlier than end time.'})
            elif date_f < utils.current_date_time():
                return jsonify({'success': False,'message': 'Date must be later than current date.'})
            elif int(capacity) <0 or float(price) < 0.0:
                return jsonify({'success': False,'message': 'Price and capacity must be greater than or equal to 0.'})
            elif int(capacity) > location_capacity['capacity']:
                return jsonify({'success': False,'message': 'Capacity must be less than or equal to location capacity.'})
            else:

                # Insert into DB
                sql = "INSERT INTO workshops (title, instructor_id, location_id, price, capacity, date, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                val = (title, instructor_id, location_id, price, capacity, date, start_time, end_time)
                cursor.execute(sql, val)
                workshop_id = cursor.lastrowid

                # Handle file upload
                file = request.files.get('image')
                if file and allowed_file(file.filename):
                    filename = f"{workshop_id}.{file.filename.rsplit('.', 1)[1]}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Create directory if it does not exist
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    file.save(file_path)

                    # Updating path to remove 'static/'
                    finalFilePath = file_path.replace("app/static/", "")
                    fixPath = finalFilePath.replace("\\", "/")

                    # Update workshop record with the new image path
                    update_sql = "UPDATE workshops SET workshop_image = %s WHERE workshop_id = %s"
                    cursor.execute(update_sql, (fixPath, workshop_id))
                else:
                    finalFilePath = 'workshops_images/workshop23.png'

                return jsonify({'success': True, 'message': 'Workshop added successfully.', 'id': workshop_id})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    else:
        return jsonify({'success': False, 'message': 'Unauthorized access.'})


@app.route('/manager/expired_subscriptions')
def expired_subscriptions():
    if 'loggedin' in session and session['loggedin']:
         cursor = utils.getCursor()
         cursor.execute('SELECT subscriptions.subscription_id,member.first_name,member.last_name, subscriptions.*\
                          FROM subscriptions\
                          JOIN member\
                          ON subscriptions.user_id = member.member_id\
                          WHERE status = \'Expired\'\
                          OR (status = \'Active\' AND end_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY));')
         subscription = cursor.fetchall()
    
         return render_template('/manager/mgr_expired_subscriptions.html', subscription=subscription, role=session['role'])
    else:
        return redirect(url_for('login'))
    
@app.route('/manager/expired_subscriptions_send_news/<int:subscription_id>')
def expired_subscriptions_send_news(subscription_id):
    if 'loggedin' in session and session['loggedin']:
         cursor = utils.getCursor()
         
         cursor.execute("SELECT * FROM subscriptions WHERE subscription_id = %s",(subscription_id,))
         sub = cursor.fetchall()
         
         if sub:
            member_id = sub[0]['user_id']
         
            title = "Pay Subscription"
            content = "Please pay your subscription because it will be expired soon or has expired."
            date = utils.current_date_time()
         
            cursor.execute("INSERT INTO news(title,content,date_published,user_id,author_id) VALUES(%s,%s,%s,%s,%s)",(title,content,date,member_id,session['id'],))   
            return redirect(url_for('view_news'))
         else:
            return redirect(url_for('expired_subscriptions')) 
    else:
        return redirect(url_for('login'))
    
@app.route('/expired_sub_search')
def expired_sub_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute('SELECT member.first_name,member.last_name, subscriptions.* FROM subscriptions JOIN member ON subscriptions.user_id = member.member_id;')
        users = cursor.fetchall()
        
        if query is None or query == '':
            return redirect(url_for('expired_subscriptions'))
        
        matched_profiles = []
        for user in users:
            if query.lower() in user['first_name'].lower():
               cursor.execute("SELECT member.first_name,member.last_name, subscriptions.* FROM subscriptions JOIN member ON subscriptions.user_id = member.member_id WHERE first_name LIKE CONCAT('%', %s, '%');",(user['first_name'],))
               member_profile_list = cursor.fetchall()
               matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['last_name'].lower():
               cursor.execute("SELECT member.first_name,member.last_name, subscriptions.* FROM subscriptions JOIN member ON subscriptions.user_id = member.member_id WHERE last_name LIKE CONCAT('%', %s, '%');",(user['last_name'],))
               member_profile_list = cursor.fetchall()
               matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['type'].lower():
                cursor.execute("SELECT member.first_name,member.last_name, subscriptions.* FROM subscriptions JOIN member ON subscriptions.user_id = member.member_id WHERE type LIKE CONCAT('%', %s, '%');",(user['type'],))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['start_date'].strftime('%Y-%m-%d').lower():
                cursor.execute("SELECT member.first_name, member.last_name, subscriptions.* FROM subscriptions JOIN member ON subscriptions.user_id = member.member_id WHERE start_date LIKE CONCAT('%', %s, '%');", (user['start_date'].strftime('%Y-%m-%d'),))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user['end_date'].strftime('%Y-%m-%d').lower():
                cursor.execute("SELECT member.first_name,member.last_name, subscriptions.* FROM subscriptions JOIN member ON subscriptions.user_id = member.member_id WHERE end_date LIKE CONCAT('%', %s, '%');",(user['end_date'].strftime('%Y-%m-%d'),))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
                
            elif query.lower() in user['status'].lower():
                cursor.execute("SELECT member.first_name,member.last_name, subscriptions.* FROM subscriptions JOIN member ON subscriptions.user_id = member.member_id WHERE status LIKE CONCAT('%', %s, '%');",(user['status'],))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
        
        if not matched_profiles:
            flash('No matching users found.', 'info')
            return redirect(url_for('expired_subscriptions'))
        else:
            return render_template("manager/mgr_expired_subscriptions.html", subscription=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))
     
@app.route('/manager/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    if 'loggedin' in session and session['loggedin']:
        
         msg = ''
         cursor = utils.getCursor()
         
         if request.method == 'POST':
              user_name = request.form['user_name']
            
              cursor.execute('SELECT * FROM instructor WHERE user_name = %s', (user_name,))
              account = cursor.fetchone()
            
              if account is not None:
                  msg = 'Account already exists!'
              elif not re.match(r'[^@]+@[^@]+\.[^@]+', request.form['email']):
                  msg = 'Invalid email address!'
              elif not re.match(r'^\d{9,12}$', request.form['phone_number']):
                   msg = 'Invalid phone number!'
              else:
                   title = request.form['title']
                   first_name = request.form['first_name']
                   last_name = request.form['last_name']
                   position = request.form['position']
                   phone_number = request.form['phone_number']
                   email = request.form['email']
                   address = request.form['address']
                   instr_profile = request.form['instructor_profile']
                   instructor_image = request.files['instructor_image']
                   password = request.form['password']
            
                   hashed_password = utils.hashing.hash_value(password , salt='schwifty')
            
                   if utils.allowed_file(instructor_image.filename):
                         filename = secure_filename(instructor_image.filename)
                         image_data = instructor_image.read()
                         cursor.execute("INSERT INTO instructor (user_name, title, first_name,last_name, position,phone_number,email,address,instructor_profile,instructor_image_name,instructor_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(user_name, title, first_name, last_name,position,phone_number,email,address,instr_profile,filename,image_data))
                         user_id =cursor.lastrowid
                         cursor.execute("INSERT INTO user (user_name,password, role, related_instructor_id) VALUES (%s, %s, %s, %s)",(user_name,hashed_password,'Instructor',user_id))
                         return redirect(url_for('instructor_profile_list'))
                   else:
                        flash("This is not a valid Image!")
                        return redirect(url_for('add_instructor'))
    
         return render_template('/manager/add_instr_profile.html', msg = msg, role=session['role'])
    else:
        return redirect(url_for('login'))
  
    
## Manager - Attendance Records - Display all records ##
@app.route('/manager/attendance')
def  mgr_attendance_records():
    if 'loggedin' in session and session.get('loggedin'):   
            
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
        print(records)
            
        return render_template('manager/mgr_attendance.html', records=records)

@app.route('/mgr_attendance_search')
def mgr_attendance_search():
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
            return redirect(url_for('mgr_attendance_records'))
        
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
            return redirect(url_for('mgr_attendance_records'))
        else:
            return render_template("manager/mgr_attendance.html", records=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))


## Manager Attendance Records as Present) ##
@app.route('/mgr_record_attendance', methods=['POST'])
def mgr_record_attendance():
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
        return redirect(url_for('mgr_attendance_records'))
    else:
        # If the user isn't logged in, redirect to the login page
        return redirect(url_for('login'))
    
    
    
## Manager Attendance Records - Undo Present ##
@app.route('/undo_attendance/<int:booking_id>', methods=['POST'])
def mgr_undo_attendance(booking_id):
    if 'loggedin' in session and session['loggedin']:
        # Update the database to record attendance as not present
        cursor = utils.getCursor()
        cursor.execute(
            'UPDATE bookings SET is_attended = FALSE WHERE booking_id = %s',
            (booking_id,)
        )
        
        utils.connection.commit()
        flash('Member marked as not present') 
        return redirect(url_for('mgr_attendance_records'))
    else:
        return redirect(url_for('login'))
    

## Manager View Payment ##
@app.route('/mgr_view_payment',methods=['GET','POST'])
def mgr_view_payment():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id;")
        payment_list = cursor.fetchall()
        
        return render_template('/manager/mgr_view_payment.html',payment_list=payment_list,role=session['role'])
          
    else:
        return redirect(url_for('login'))
    

@app.route('/mgr_view_payment_search')
def mgr_view_payment_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id;")
        payments = cursor.fetchall()

        if query is None or query == '':
            return redirect(url_for('mgr_view_payment'))
        
        matched_profiles = []
            
        for payment in payments:
            payment_id = str(payment['payment_id'])
            amount = str(payment['amount'])
            if query.lower() in payment_id.lower():
               cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id WHERE p.payment_id LIKE CONCAT('%', %s, '%');", (payment_id,))
               payment_list = cursor.fetchall()
               matched_profiles.extend(payment_list)
            
            elif query.lower() in payment['payment_type'].lower():
               cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id WHERE p.payment_type LIKE CONCAT('%', %s, '%');",(payment['payment_type'],))
               payment_list = cursor.fetchall()
               matched_profiles.extend(payment_list)
               
            elif query.lower() in payment['payment_date'].strftime('%Y-%m-%d').lower():
               cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id WHERE p.payment_date LIKE CONCAT('%', %s, '%');", (payment['payment_date'].strftime('%Y-%m-%d'),))
               payment_list = cursor.fetchall()
               matched_profiles.extend(payment_list)
               
            elif query.lower() in payment['user_name'].lower():
               cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id WHERE u.user_name LIKE CONCAT('%', %s, '%');", (payment['user_name'],))
               payment_list = cursor.fetchall()
               matched_profiles.extend(payment_list)

            elif query.lower() in amount.lower():
               cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id WHERE p.amount LIKE CONCAT('%', %s, '%');", (amount,))
               payment_list = cursor.fetchall()
               matched_profiles.extend(payment_list)

            elif query.lower() in payment['status'].lower():
               cursor.execute("SELECT p.payment_id, u.user_name, CONCAT(m.first_name, ' ', m.last_name) AS member_name, p.amount, p.payment_type, p.payment_date, p.status FROM payments p JOIN user u ON p.user_id = u.user_id JOIN member m ON u.related_member_id = m.member_id WHERE p.status LIKE CONCAT('%', %s, '%');",(payment['status'],))
               payment_list = cursor.fetchall()
               matched_profiles.extend(payment_list)

        if not matched_profiles:
            flash('No matching payments found.', 'info')
            return redirect(url_for('mgr_view_payment'))
        else:
            return render_template("manager/mgr_view_payment.html", payment_list=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))
     

#manager view member subscriptions
@app.route('/mgr_view_member_sub',methods=['GET','POST'])
def mgr_view_member_sub():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id \
                        FROM subscriptions\
                        JOIN member ON member.member_id = subscriptions.user_id;")
        sub_list = cursor.fetchall()
        
        return render_template('/manager/mgr_member_subscription.html',sub_list=sub_list,role=session['role'])
          
    else:
        return redirect(url_for('login'))
    
@app.route('/mgr_view_sub_search')
def mgr_view_sub_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status ,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id;")
        subs = cursor.fetchall()

        if query is None or query == '':
            return redirect(url_for('mgr_view_member_sub'))
        
        matched_profiles = []
            
        for sub in subs:
            start_date = str(sub['start_date'])
            end_date = str(sub['end_date'])
            
            user_name = sub['user_name']
            first_name = sub['first_name']
            last_name = sub['last_name']
            if query.lower() in user_name.lower():
               cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE member.user_name LIKE CONCAT('%', %s, '%');", (user_name,))
               sub_list = cursor.fetchall()
               matched_profiles.extend(sub_list)
            

            elif query.lower() in sub['first_name'].lower():
               cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE member.first_name LIKE CONCAT('%', %s, '%');",(first_name,))
               sub_list = cursor.fetchall()
               matched_profiles.extend(sub_list)
             
            elif query.lower() in sub['last_name'].lower():
               cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE member.last_name LIKE CONCAT('%', %s, '%');",(last_name,))
               sub_list = cursor.fetchall()
               matched_profiles.extend(sub_list) 
               
            elif query.lower() in sub['type'].lower():
               cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE subscriptions.type LIKE CONCAT('%', %s, '%');",(sub['type'],))
               sub_list = cursor.fetchall()
               matched_profiles.extend(sub_list)  
               
            elif query.lower() in sub['status'].lower():
               cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE subscriptions.status LIKE CONCAT('%', %s, '%');",(sub['status'],))
               sub_list = cursor.fetchall()
               matched_profiles.extend(sub_list)
             
            elif query.lower() in start_date.lower():
               cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE subscriptions.start_date LIKE CONCAT('%', %s, '%');",(start_date,))
               sub_list = cursor.fetchall()
               matched_profiles.extend(sub_list)  
            
            elif query.lower() in end_date.lower():
               cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE subscriptions.end_date LIKE CONCAT('%', %s, '%');",(end_date,))
               sub_list = cursor.fetchall()
               matched_profiles.extend(sub_list)
                          

        if not matched_profiles:
            flash('No matching member subscriptions found.', 'info')
            return redirect(url_for('mgr_view_member_sub'))
        else:
            return render_template("manager/mgr_member_subscription.html", sub_list=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))

## Manager edit member subscription  ## 
@app.route('/manager/edit_member_sub/<int:sub_id>', methods=['GET', 'POST'])
def edit_member_sub(sub_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        if request.method == 'POST':
            
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            type = request.form.get('type')
            status = request.form.get('status')
            
            date_f = datetime.strptime(end_date, '%Y-%m-%d')
            
            if date_f < utils.current_date_time() and status == 'Active':
                flash('End date cannot be in the past.', 'info')
                return redirect(url_for('edit_member_sub', sub_id=sub_id))
            else:
               cursor.execute("UPDATE subscriptions SET start_date = %s, end_date = %s, type = %s, status = %s WHERE subscription_id = %s",(start_date, end_date, type, status,sub_id,))
            
               return redirect(url_for('mgr_view_member_sub'))
        
        else:
            cursor.execute("SELECT member.user_name,member.first_name,member.last_name,subscriptions.start_date,subscriptions.end_date,subscriptions.type,subscriptions.status,subscriptions.subscription_id FROM subscriptions JOIN member ON member.member_id = subscriptions.user_id WHERE subscriptions.subscription_id = %s",(sub_id,))
            sub = cursor.fetchone()
            return render_template('manager/edit_member_subscription.html', sub=sub, role=session['role'])    
            
            
        
       
    else:
        return redirect(url_for('login'))
    
    
  
## Manager delete member subscription  ##    
@app.route('/manager/delete_member_sub/<int:sub_id>')
def delete_member_sub(sub_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM subscriptions WHERE subscription_id=%s',(sub_id,))
        
        return redirect(url_for('mgr_view_member_sub'))
    else:
        return redirect(url_for('login'))