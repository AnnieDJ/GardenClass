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
        
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM manager WHERE user_name = %s", (session['username'],))
        
        manager_profile = cursor.fetchone()
        
        return render_template('/manager/managerprofile.html', manager_profile = manager_profile, role=session['role'])
        
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
            gardering_experience = request.form.get('gardering_experience')
            
            cursor.execute("UPDATE manager SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s, gardering_experience = %s \
                WHERE user_name = %s", (title, first_name, last_name, position, phone_number, email, gardering_experience, session['username'],))

            return redirect(url_for('manager_profile'))
        else:
            cursor.execute("SELECT * FROM manager WHERE user_name = %s", (session['username'],))
            manager_profile = cursor.fetchone()
        
            return render_template('/manager/editmanagerprofile.html', manager_profile = manager_profile, role=session['role'])
        
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
            if instructor[10] is not None and instructor[10] != '':
               image_encode = base64.b64encode(instructor[11]).decode('utf-8')
               encoded_instructor_profile.append((instructor[0], instructor[1],instructor[2] ,instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],image_encode))
            else:
                encoded_instructor_profile.append((instructor[0], instructor[1],instructor[2],instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],None))
            
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
               
               if instructor_image and utils.allowed_file(instructor_image.filename):
                   
                   filename = secure_filename(instructor_image.filename)
                   image_data = instructor_image.read()
                   cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s,  address = %s, instructor_profile = %s, instructor_image_name = %s, instructor_image = %s WHERE instructor_id = %s",(title,first_name,last_name,position,phone_number,email,address,instructor_profile,filename,image_data,instructor_id,))
                   cursor.execute("UPDATE user SET password = %s WHERE related_instructor_id = %s",(hashed_password,instructor_id,))
                   
               else:
                   cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s,  address = %s, instructor_profile = %s WHERE instructor_id = %s",(title,first_name,last_name,position,phone_number,email,address,instructor_profile,instructor_id,))
                   cursor.execute("UPDATE user SET password = %s WHERE related_instructor_id = %s",(hashed_password,instructor_id,))
            else:
                if instructor_image and utils.allowed_file(instructor_image.filename):
                   
                   filename = secure_filename(instructor_image.filename)
                   image_data = instructor_image.read()
                   cursor.execute("UPDATE instructor SET title = %s, first_name = %s, last_name = %s, position = %s, phone_number = %s, email = %s,  address = %s, instructor_profile = %s, instructor_image_name = %s, instructor_image = %s WHERE instructor_id = %s",(title,first_name,last_name,position,phone_number,email,address,instructor_profile,filename,image_data,instructor_id,))
                   
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
            if query.lower() in user[0].lower():
               cursor.execute("SELECT * FROM instructor WHERE user_name LIKE CONCAT('%', %s, '%');",(user[0],))
               instructor_profile_list = cursor.fetchall()
             
               for instructor in instructor_profile_list:
                   if instructor[10] is not None and instructor[10] != '':
                      image_encode = base64.b64encode(instructor[11]).decode('utf-8')
                      results.append((instructor[0], instructor[1],instructor[2] ,instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],image_encode))
                   else:
                      results.append((instructor[0], instructor[1],instructor[2],instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],None))
            
               return render_template("manager/manage_instr_profile.html", instructor_profile=results, role = session['role'])
           
            elif query.lower() in user[1].lower():
               cursor.execute("SELECT * FROM instructor WHERE email LIKE CONCAT('%', %s, '%');",(user[1],))
               instructor_profile_list = cursor.fetchall()
              
               for instructor in instructor_profile_list:
                   if instructor[10] is not None and instructor[10] != '':
                      image_encode = base64.b64encode(instructor[11]).decode('utf-8')
                      results.append((instructor[0], instructor[1],instructor[2] ,instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],image_encode))
                   else:
                      results.append((instructor[0], instructor[1],instructor[2],instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],None))
            
               return render_template("manager/manage_instr_profile.html", instructor_profile=results, role = session['role'])
           
            elif query.lower() in user[2].lower():
                cursor.execute("SELECT * FROM instructor WHERE address LIKE CONCAT('%', %s, '%');",(user[2],))
                instructor_profile_list = cursor.fetchall()
                
                for instructor in instructor_profile_list:
                   if instructor[10] is not None and instructor[10] != '':
                      image_encode = base64.b64encode(instructor[11]).decode('utf-8')
                      results.append((instructor[0], instructor[1],instructor[2] ,instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],image_encode))
                   else:
                      results.append((instructor[0], instructor[1],instructor[2],instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],None))
            
                return render_template("manager/manage_instr_profile.html", instructor_profile=results, role = session['role'])
            
            elif query.lower() in user[3].lower():
                cursor.execute("SELECT * FROM instructor WHERE position LIKE CONCAT('%', %s, '%');",(user[3],))
                instructor_profile_list = cursor.fetchall()
                
                for instructor in instructor_profile_list:
                   if instructor[10] is not None and instructor[10] != '':
                      image_encode = base64.b64encode(instructor[11]).decode('utf-8')
                      results.append((instructor[0], instructor[1],instructor[2] ,instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],image_encode))
                   else:
                      results.append((instructor[0], instructor[1],instructor[2],instructor[3], instructor[4], instructor[5],instructor[6],instructor[7],instructor[8],instructor[9],instructor[10],None))
            
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
            if query.lower() in user[0].lower():
               cursor.execute("SELECT * FROM member WHERE user_name LIKE CONCAT('%', %s, '%');",(user[0],))
               member_profile_list = cursor.fetchall()
               matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user[1].lower():
               cursor.execute("SELECT * FROM member WHERE email LIKE CONCAT('%', %s, '%');",(user[1],))
               member_profile_list = cursor.fetchall()
               matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user[2].lower():
                cursor.execute("SELECT * FROM member WHERE address LIKE CONCAT('%', %s, '%');",(user[2],))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
            
            elif query.lower() in user[3].lower():
                cursor.execute("SELECT * FROM member WHERE position LIKE CONCAT('%', %s, '%');",(user[3],))
                member_profile_list = cursor.fetchall()
                matched_profiles.extend(member_profile_list)
        
        if not matched_profiles:
            flash('No matching users found.', 'info')
            return redirect(url_for('member_profile_list'))
        else:
            return render_template("manager/manage_member_profile.html", member_profile=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))
