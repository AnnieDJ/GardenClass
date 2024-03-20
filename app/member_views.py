from app import app
from flask import render_template, redirect, url_for
from flask import session,request
from app import utils

## Member dashboard ##
@app.route('/member/dashboard')
def member_dashboard():
    if 'loggedin' in session and session['loggedin']:
        return render_template('/member/member_dashboard.html', username=session['username'], role=session['role'])


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
        
            cursor.execute("UPDATE member SET title = %s, first_name = %s,  last_name = %s, phone_number = %s, email = %s,address = %s, \
                           date_of_birth = %s WHERE user_name = %s", (title, first_name, last_name,phone_number, email, address,date_of_birth,session['username'],))       
          
            return redirect(url_for('member_profile'))
        else:
            cursor.execute("SELECT * FROM member WHERE user_name = %s", (session['username'],))
            member_profile = cursor.fetchone()
        
            return render_template('/member/editmemberprofile.html', member_profile = member_profile, role=session['role'])
        
    else:
        return redirect(url_for('login'))
