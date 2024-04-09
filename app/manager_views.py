from app import app
from flask import render_template,redirect,url_for, g
from flask import session,request,jsonify,flash
from app import utils
from werkzeug.utils import secure_filename
import base64
import re
from datetime import datetime
import mysql.connector

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
            if manager_profile['manager_image_name'] is not None and manager_profile['manager_image_name'] != '':
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
            if instructor['instructor_image_name'] is not None and instructor['instructor_image_name'] != '':
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
        cursor.execute("SELECT * FROM member;")
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
                   
            else: 
               cursor.execute("UPDATE member SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, address = %s, date_of_birth = %s, subscription_date = %s, type = %s, expiry_date = %s WHERE member_id = %s",(title,first_name,last_name,position,phone_number,email,address,date_of_birth,subscription_date, type,expiry_date,member_id,))
             
            return redirect(url_for('member_profile_list'))
            
        else:
            cursor.execute('SELECT * FROM member WHERE member_id = %s;',(member_id,))      
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
        
        
        
            cursor = utils.getCursor()

        
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
                
                print(f"An error occurred: {e}")
                return jsonify({'success': False, 'message': 'Database update error.'})
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
        
        
        
            cursor = utils.getCursor()

        
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
                
                print(f"An error occurred: {e}")
                return jsonify({'success': False, 'message': 'Database update error.'})
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
        cursor.execute("DELETE FROM one_on_one_lessons WHERE lesson_id = %s", (lesson_id,))
       
        return jsonify({'success': True, 'message': 'One-on-one lesson deleted successfully.'})
    except Exception as e:
        
        return jsonify({'success': False, 'message': f'Failed to delete one-on-one lesson. Error: {e}'})


@app.route('/delete_group_lesson/<int:lesson_id>', methods=['POST'])
def delete_group_lesson(lesson_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'You must be logged in to perform this action.'}), 401
    try:
            cursor = utils.getCursor()
            # Execute the SQL command to delete the lesson
            cursor.execute("DELETE FROM lessons WHERE lesson_id = %s", (lesson_id,))
            
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
        SELECT w.*, i.first_name, i.last_name FROM workshops w
        JOIN instructor i ON w.instructor_id = i.instructor_id
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
        
        price = request.form.get('price')
        capacity = request.form.get('capacity')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
		
        start_time_obj = datetime.strptime(start_time, "%H:%M" if len(start_time) <= 5 else "%H:%M:%S")
        end_time_obj = datetime.strptime(end_time, "%H:%M" if len(end_time) <= 5 else "%H:%M:%S")
      
        start_time_formatted = start_time_obj.strftime("%H:%M:%S")
        end_time_formatted = end_time_obj.strftime("%H:%M:%S")
        workshop_image = request.form.get('workshop_image')
        cursor = utils.getCursor()

        update_query = """
        UPDATE workshops
        SET date = %s, start_time = %s, end_time = %s, location_id = %s, capacity = %s, price = %s, workshop_image = %s
        WHERE workshop_id = %s
        """
        update_values = (date, start_time_formatted, end_time_formatted, location_id, capacity, price, workshop_image,workshop_id)

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
        cursor.execute("DELETE FROM workshops WHERE workshop_id = %s", (workshop_id,))
        return redirect(url_for('manager_workshops'))
    else:
        return redirect(url_for('login'))
    
@app.route('/manager/add_workshop', methods=['POST'])
def add_workshop():
    if 'loggedin' in session and session['role'] == 'Manager':
        try:
            
            title = request.form.get('title')
            instructor_id = request.form.get('instructor_id')
            location_id = request.form.get('location_id')
            price = request.form.get('price')
            capacity = request.form.get('capacity')
            date = request.form.get('addDate')
            start_time = request.form.get('starttime')
            end_time = request.form.get('endtime')
            workshop_image = 'workshops_images/workshop1.png'  

            cursor = utils.getCursor()

           
            sql = "INSERT INTO workshops (title, instructor_id, location_id, price, capacity, date, start_time, end_time, workshop_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (title, instructor_id, location_id, price, capacity, date, start_time, end_time, workshop_image)

           
            cursor.execute(sql, val)
         

            return jsonify({'success': True, 'message': 'Workshop added successfully.'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    else:
        return jsonify({'success': False, 'message': 'Unauthorized access.'})
    

@app.route('/manager/expired_subscriptions', methods=['GET', 'POST'])
def expired_subscriptions():
    if 'loggedin' in session and session['loggedin']:
         cursor = utils.getCursor()
         cursor.execute('SELECT member.first_name,member.last_name, subscriptions.*\
                          FROM subscriptions\
                          JOIN member\
                          ON subscriptions.user_id = member.member_id\
                          WHERE status = \'Expired\'\
                          OR (status = \'Active\' AND end_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY));')
         subscription = cursor.fetchall()
    
         return render_template('/manager/mgr_expired_subscriptions.html', subscription=subscription, role=session['role'])
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