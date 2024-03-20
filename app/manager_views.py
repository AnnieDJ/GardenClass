from app import app
from flask import render_template,redirect,url_for
from flask import session,request,jsonify
from app import utils
from werkzeug.utils import secure_filename
import base64

@app.route('/manager/dashboard')
def manager_dashboard():
    if 'loggedin' in session and session['loggedin']:
        return render_template("/manager/mgr_dashboard.html", username=session['username'], role=session['role'])

@app.route('/manager/profile')
def manager_profile():
    return "Manager Profile"


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
    
@app.route('/manager/delete_instructor_profile/<int:instructor_id>')
def delete_instructor_profile(instructor_id):
    
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM instructor WHERE instructor_id=%s',(instructor_id,))
        cursor.execute('DELETE FROM user WHERE related_instructor_id=%s',(instructor_id,))
        
        return redirect(url_for('instructor_profile_list'))
    else:
        return redirect(url_for('login'))

@app.route('/manager/member_profile_list')
def member_profile_list():
    
    if 'loggedin' in session and session['loggedin']: 
        
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM member;")
        member_profile = cursor.fetchall()
        
            
        return render_template("manager/manage_member_profile.html", member_profile=member_profile, role = session['role'])
    else:
        return redirect(url_for('login'))
    
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
    
    
  
