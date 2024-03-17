from app import app
from flask import render_template, redirect, url_for
from flask import session
from app import utils

@app.route('/member/dashboard')
def member_dashboard():
    if 'loggedin' in session and session['loggedin']:
        return render_template('/member/memberdashboard.html', username=session['username'], role=session['role'])

@app.route('/member/profile')
def member_profile():
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM member WHERE user_name = %s", (session['username'],))
        
        member_profile = cursor.fetchone()
        
        return render_template('/member/memberprofile.html', member_profile = member_profile, role=session['role'])
        
    else:
        return redirect(url_for('login'))
    
    
@app.route('/member/member_edit_profile', methods=['GET', 'POST'])
def member_edit_profile():
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM member WHERE user_name = %s", (session['username'],))
        
        member_profile = cursor.fetchone()
        
        return render_template('/member/memberprofile.html', member_profile = member_profile, role=session['role'])
        
    else:
        return redirect(url_for('login'))
    
        