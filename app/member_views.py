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
            ool_query = """SELECT * FROM `one-on-one lessons` 
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
    