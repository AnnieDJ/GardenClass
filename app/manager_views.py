from app import app
from flask import render_template,redirect,url_for
from flask import session,request,jsonify,flash
from app import utils
from werkzeug.utils import secure_filename
import base64

## Manager Dashboard ##
@app.route('/manager/dashboard')
def manager_dashboard():
    if 'loggedin' in session and session['loggedin']:
        return render_template("/manager/mgr_dashboard.html", username=session['username'], role=session['role'])



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
            
            if manager_image:
                
                if utils.allowed_file(manager_image.filename):
                    filename = secure_filename(manager_image.filename)
                    image_data = manager_image.read()
                    
                    cursor.execute("UPDATE manager SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, gardering_experience = %s, manager_image_name = %s, profile_image = %s  \
                        WHERE user_name = %s", (title, first_name, last_name, position, phone_number, email, gardering_experience, filename,image_data, session['username'],))
                    
                else:
                    flash('Invalid file type, please upload a valid image file')
                    
                return redirect(url_for('manager_profile'))
                    
            else:
                cursor.execute("UPDATE manager SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, gardering_experience = %s \
                   WHERE user_name = %s", (title, first_name, last_name, position, phone_number, email, gardering_experience, session['username'],))

                return redirect(url_for('manager_profile'))
        else:
            cursor.execute("SELECT * FROM manager WHERE user_name = %s", (session['username'],))
            manager_profile = cursor.fetchone()
        
            return render_template('/manager/edit_mgr_profile.html', manager_profile = manager_profile, role=session['role'])
        
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
        
       # return any(email == row[0] for row in email_list)
        if any(email == row[0] for row in email_list):
          return jsonify({'valid': False})
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

   
   
@app.route('/another/route/using/manager_dashboard')
def manager_dashboard_different():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM lessons ORDER BY date, start_time LIMIT 2")
        lesson_data = cursor.fetchall()
        cursor.execute("SELECT * FROM workshops ORDER BY date, start_time LIMIT 2")
        workshop_data = cursor.fetchall()
        cursor.execute("SELECT * FROM news ORDER BY date_published LIMIT 1")
        news_data = cursor.fetchall()
        
        cursor.close()
        # Make sure the username and role are set in the session as well
        return render_template("manager/mgr_dashboard.html", lessons=lesson_data,workshops=workshop_data, news=news_data, username=session['username'], role=session['role'])
    
    else:
        return redirect(url_for('login'))


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
        ool_query = f"""SELECT o.*, m.user_name, m.first_name, m.last_name FROM `one-on-one lessons` o 
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

