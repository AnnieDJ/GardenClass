from app import app
from flask import render_template,redirect,url_for
from flask import session
from app import utils

@app.route('/instructor/dashboard')
def instructor_dashboard():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()

        # Retrieve the current logged-in user's username
        user_name = session['username']
        
        # First, get the related_instructor_id from the User table
        cursor.execute("SELECT related_instructor_id FROM User WHERE user_name = %s", (user_name,))
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


@app.route('/instructor/profile')
def instructor_profile():
     return render_template("/instructor/instr_profile.html", username=session['username'], role=session['role'])

@app.route('/instructor/lessons')
def instructor_lessons():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()

        # 获取当前登录用户的user_name
        user_name = session['username']
        
        # 从User表中获取related_instructor_id
        cursor.execute("SELECT related_instructor_id FROM User WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            return "Instructor ID not found for the current user", 404

        related_instructor_id = result['related_instructor_id']

        # 使用related_instructor_id查询lessons表
        cursor.execute("SELECT * FROM lessons WHERE instructor_id = %s", (related_instructor_id,))
        lessons_data = cursor.fetchall()
      
        cursor.close()
        return render_template("/instructor/instr_lessons.html", lessons=lessons_data)
    else:
        return redirect(url_for('login'))


      
        # Make sure the username and role are set in the session as well
        