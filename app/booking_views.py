from app import app
from app import utils
from flask import Flask, render_template, jsonify,redirect,url_for,flash
import json
import datetime
from flask import session,request


#Showing the calendar
@app.route('/courses')
def get_courses():
    if 'loggedin' in session and session['loggedin']:
        return  render_template('/booking/booking_calendar.html',role=session['role'])
    else:
        return redirect(url_for('login'))

#getting courses and make a booking
@app.route('/get_course_info')
def get_course_info():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('SELECT lessons.lesson_id as course_id,instructor.first_name as instr_first, instructor.last_name as instr_last,lessons.title, lessons.date, lessons.start_time,lessons.end_time,locations.name as location,locations.address,\'lesson\' as type\
                    FROM lessons \
                    JOIN instructor ON lessons.instructor_id = instructor.instructor_id\
                    JOIN locations ON locations.location_id = lessons.location_id\
                    UNION\
                    SELECT workshops.workshop_id as course_id,instructor.first_name as instr_first, instructor.last_name as instr_last,workshops.title, workshops.date, workshops.start_time,workshops.end_time ,locations.name as location,locations.address,\'workshop\' as type\
                    FROM workshops \
                    JOIN instructor ON workshops.instructor_id = instructor.instructor_id\
                    JOIN locations ON locations.location_id = workshops.location_id;')
        courses = cursor.fetchall()
        course_data = []
        for course in courses:
            start_time = datetime.datetime.combine(course['date'], datetime.datetime.min.time()) + course['start_time']
            end_time = datetime.datetime.combine(course['date'], datetime.datetime.min.time()) + course['end_time']
        
            course_id = course['course_id']
            title = course['type'] +': '+course['title'] 
            instructor_name = course['instr_first'] + ' ' + course['instr_last']
            address = course['location']+': '+course['address']
            type = course['type']
        
            course_data.append({
                 'title': title,  
                 'start': start_time.isoformat(),  
                 'end': end_time.isoformat(),
                 'instructor':instructor_name,
                 'location':address,
                 'course_id':course_id,
                 'type': type,
                 'classNames': 'lesson' if type == 'lesson' else 'workshop'
               })
            
        return jsonify(course_data)
    else:
        return redirect(url_for('login'))
    
@app.route('/get_workshop_mainpage')
def get_workshop_mainpage():
        cursor = utils.getCursor()
        cursor.execute('SELECT workshops.workshop_id as course_id,instructor.first_name as instr_first, instructor.last_name as instr_last,workshops.title, workshops.date, workshops.start_time,workshops.end_time ,locations.name as location,locations.address,\'workshop\' as type\
                        FROM workshops \
                        JOIN instructor ON workshops.instructor_id = instructor.instructor_id\
                        JOIN locations ON locations.location_id = workshops.location_id;')
        courses = cursor.fetchall()
        course_data = []
        for course in courses:
            start_time = datetime.datetime.combine(course['date'], datetime.datetime.min.time()) + course['start_time']
            end_time = datetime.datetime.combine(course['date'], datetime.datetime.min.time()) + course['end_time']
        
            course_id = course['course_id']
            title = course['type'] +': '+course['title'] 
            instructor_name = course['instr_first'] + ' ' + course['instr_last']
            address = course['location']+': '+course['address']
            type = course['type']
        
            course_data.append({
                 'title': title,  
                 'start': start_time.isoformat(),  
                 'end': end_time.isoformat(),
                 'instructor':instructor_name,
                 'location':address,
                 'course_id':course_id,
                 'type': type
               })
                 
        return jsonify(course_data)
  
@app.route('/booking_course/<string:course_type>/<int:course_id>', methods=['GET', 'POST'])
def booking_course(course_type, course_id):
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        disabled = False
        msg = ''
        if course_type == 'lesson':
           cursor.execute('SELECT * FROM bookings WHERE user_id = %s AND lesson_id = %s AND status = %s;',(session['id'], course_id,'Booked',))
           exist_bookings = cursor.fetchall()          
           
           cursor.execute('SELECT lessons.lesson_id as course_id,instructor.first_name as instr_first, instructor.last_name as instr_last,lessons.title, lessons.date, lessons.start_time,lessons.end_time,locations.name as location,locations.address,lessons.capacity\
                           FROM lessons \
                          JOIN instructor ON lessons.instructor_id = instructor.instructor_id\
                          JOIN locations ON locations.location_id = lessons.location_id\
                          WHERE lessons.lesson_id = %s;',(course_id,)) 
           course = cursor.fetchone()
           
           cursor.fetchall()
           
           cursor.execute('SELECT COUNT(booking_id) as num FROM bookings WHERE lesson_id = %s AND status = %s GROUP BY lesson_id;',(course_id,'Booked',))
           booking_number = cursor.fetchone()
           cursor.fetchall()
       
           if exist_bookings:
              disabled = True
              msg = 'You have already booked this lesson'
              if request.method == 'POST' and request.form['action'] == 'cancel':
                 return redirect(url_for('get_courses'))
              return render_template('/booking/booking_course.html',course=course,booking_number=booking_number,role=session['role'],disabled = disabled,msg = msg) 
          
           if booking_number and booking_number['num'] >= course['capacity']:
              disabled = True
              msg = 'This lesson is full'
              if request.method == 'POST' and request.form['action'] == 'cancel':
                 return redirect(url_for('get_courses'))
              return render_template('/booking/booking_course.html',course=course,booking_number=booking_number,role=session['role'],disabled = disabled,msg = msg)   
           
           if request.method == 'POST' and request.form['action'] == 'confirm':
              cursor.execute('INSERT INTO bookings (user_id,lesson_id,booking_type,status) VALUES(%s,%s,%s,%s)',(session['id'],course['course_id'],'Lesson','Booked',))
              return redirect(url_for('member_pay_lesson',lesson_id = course['course_id']))
        
           elif request.method == 'POST' and request.form['action'] == 'cancel':
                return redirect(url_for('get_courses'))
        
           return render_template('/booking/booking_course.html',course=course,booking_number=booking_number,role=session['role'],disabled = disabled,msg = msg)
            
        else:
           cursor.execute('SELECT * FROM bookings WHERE user_id = %s AND workshop_id = %s AND status = %s;',(session['id'], course_id,'Booked',))
           exist_bookings = cursor.fetchall() 
           
           cursor.execute('SELECT workshops.workshop_id as course_id,instructor.first_name as instr_first, instructor.last_name as instr_last,workshops.title, workshops.date, workshops.start_time,workshops.end_time ,locations.name as location,locations.address,workshops.capacity\
                    FROM workshops \
                    JOIN instructor ON workshops.instructor_id = instructor.instructor_id\
                    JOIN locations ON locations.location_id = workshops.location_id\
                    WHERE workshops.workshop_id = %s;',(course_id,))  
                  
           course = cursor.fetchone()           
           cursor.fetchall()
                    
           cursor.execute('SELECT COUNT(booking_id) as num FROM bookings WHERE workshop_id = %s AND status = %s  GROUP BY workshop_id;',(course_id,'Booked',))
           booking_number = cursor.fetchone()
           cursor.fetchall()
           
           if exist_bookings:
              disabled = True
              msg = 'You have already booked this workshop'
              if request.method == 'POST' and request.form['action'] == 'cancel':
                 return redirect(url_for('get_courses'))
              return render_template('/booking/booking_course.html',course=course,booking_number=booking_number,role=session['role'],disabled = disabled,msg = msg)  
          
           if booking_number and booking_number['num'] >= course['capacity']:
              disabled = True
              msg = 'This workshop is full'
              if request.method == 'POST' and request.form['action'] == 'cancel':
                 return redirect(url_for('get_courses'))
              return render_template('/booking/booking_course.html',course=course,booking_number=booking_number,role=session['role'],disabled = disabled,msg = msg) 
           
           if request.method == 'POST' and request.form['action'] == 'confirm':
              cursor.execute('INSERT INTO bookings (user_id,workshop_id,booking_type,status) VALUES(%s,%s,%s,%s)',(session['id'],course['course_id'],'Workshop','Booked',))
              return redirect(url_for('member_pay_workshop',workshop_id = course['course_id']))
        
           elif request.method == 'POST' and request.form['action'] == 'cancel':
                return redirect(url_for('get_courses'))
            
           return render_template('/booking/booking_course.html',course=course,booking_number=booking_number,role=session['role'],disabled = disabled,msg = msg)
           
    else:
        return redirect(url_for('login'))
    
@app.route('/view_mybookings')
def view_mybookings():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('SELECT booking_id,title,booking_type,status FROM bookings JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                        UNION\
                        SELECT booking_id,title,booking_type,status FROM bookings JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                        UNION\
                        SELECT booking_id,lesson_name,booking_type,bookings.status FROM bookings JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                        WHERE user_id =%s;',(session['id'],))
        my_bookings = cursor.fetchall()
        
        return render_template('/booking/member_booking_content.html',my_bookings=my_bookings,role=session['role'])
    else:
        return redirect(url_for('login'))
@app.route('/cancel_booking/<int:booking_id>',methods=['GET','POST'])
def cancel_booking(booking_id):
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        if request.method == 'POST':
           cursor.execute('UPDATE bookings SET status= %s WHERE booking_id = %s',('Cancelled',booking_id,))
        return redirect(url_for('view_mybookings'))
    else:
        return redirect(url_for('login'))
    
@app.route('/view_booking')
def view_booking():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type,member.user_name,member.first_name,member.last_name,bookings.status\
                         FROM bookings\
                         JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                         JOIN locations ON workshops.location_id = locations.location_id\
                         JOIN member ON member.member_id = bookings.user_id\
                         UNION\
                         SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type,member.user_name,member.first_name,member.last_name,bookings.status\
                         FROM bookings\
                         JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                         JOIN locations ON lessons.location_id = locations.location_id\
                         JOIN member ON member.member_id = bookings.user_id\
                         UNION\
                         SELECT bookings.booking_id,one_on_one_lessons.lesson_name as title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type,member.user_name,member.first_name,member.last_name,bookings.status\
                         FROM bookings\
                         JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                         JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                         JOIN member ON member.member_id = bookings.user_id;')
        booking_list = cursor.fetchall()
        
        return render_template('/booking/view_booking.html',booking_list=booking_list,role=session['role'])
          
    else:
        return redirect(url_for('login'))
    
@app.route('/delete_booking/<int:booking_id>')
def delete_booking(booking_id):
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM bookings WHERE booking_id = %s',(booking_id,))
        
        return redirect(url_for('view_booking'))
    else:
        return redirect(url_for('login'))
    
@app.route('/edit_booking/<int:booking_id>',methods=['GET','POST'])
def edit_booking(booking_id):
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM bookings WHERE booking_id = %s',(booking_id,))
        booking_item = cursor.fetchone()
        cursor.fetchall()
        
        if request.method == 'POST':
           status = request.form.get('status')
           cursor.execute('UPDATE bookings SET status= %s WHERE booking_id = %s',(status,booking_id,))
           return redirect(url_for('view_booking'))
       
        return render_template('booking/edit_booking.html',booking_item=booking_item,role=session['role'])      
    else:
        return redirect(url_for('login'))

@app.route('/bookings_search')
def bookings_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute('SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type,member.user_name,member.first_name,member.last_name\
                         FROM bookings\
                         JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                         JOIN locations ON workshops.location_id = locations.location_id\
                         JOIN member ON member.member_id = bookings.user_id\
                         UNION\
                         SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type,member.user_name,member.first_name,member.last_name\
                         FROM bookings\
                         JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                         JOIN locations ON lessons.location_id = locations.location_id\
                         JOIN member ON member.member_id = bookings.user_id\
                         UNION\
                         SELECT bookings.booking_id,one_on_one_lessons.lesson_name as title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type,member.user_name,member.first_name,member.last_name\
                         FROM bookings\
                         JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                         JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                         JOIN member ON member.member_id = bookings.user_id;')
        bookings = cursor.fetchall()
        
        if query is None or query == '':
            return redirect(url_for('view_booking'))
        
        matched_profiles = []
            
        for booking in bookings:
            if query.lower() in booking['title'].lower():
               cursor.execute("SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                               JOIN locations ON workshops.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE workshops.title LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                               JOIN locations ON lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE lessons.title LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,one_on_one_lessons.lesson_name AS title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                               JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE one_on_one_lessons.lesson_name LIKE CONCAT('%', %s, '%');",(booking['title'],booking['title'],booking['title'],))
               booking_list = cursor.fetchall()
               matched_profiles.extend(booking_list)
            
            elif query.lower() in booking['booking_type'].lower():
               cursor.execute("SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                               JOIN locations ON workshops.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE bookings.booking_type LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                               JOIN locations ON lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE bookings.booking_type LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,one_on_one_lessons.lesson_name AS title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                               JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE bookings.booking_type LIKE CONCAT('%', %s, '%');",(booking['booking_type'],booking['booking_type'],booking['booking_type'],))
               booking_list = cursor.fetchall()
               matched_profiles.extend(booking_list)
               
            elif query.lower() in booking['address'].lower():
               cursor.execute("SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                               JOIN locations ON workshops.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE locations.address LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                               JOIN locations ON lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE locations.address LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,one_on_one_lessons.lesson_name AS title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                               JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE locations.address LIKE CONCAT('%', %s, '%');",(booking['address'],booking['address'],booking['address'],))
               booking_list = cursor.fetchall()
               matched_profiles.extend(booking_list)
            
            elif query.lower() in str(booking['capacity']):
               cursor.execute("SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                               JOIN locations ON workshops.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE workshops.capacity LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                               JOIN locations ON lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE lessons.capacity LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,one_on_one_lessons.lesson_name AS title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                               JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE capacity LIKE CONCAT('%', %s, '%');",(str(booking['capacity']),str(booking['capacity']),str(booking['capacity']),))
               booking_list = cursor.fetchall()
               matched_profiles.extend(booking_list)
               
            elif query.lower() in booking['date'].strftime('%Y-%m-%d').lower():
               cursor.execute("SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                               JOIN locations ON workshops.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE workshops.date LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                               JOIN locations ON lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE lessons.date LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,one_on_one_lessons.lesson_name AS title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                               JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE one_on_one_lessons.date LIKE CONCAT('%', %s, '%');",(booking['date'].strftime('%Y-%m-%d'),booking['date'].strftime('%Y-%m-%d'),booking['date'].strftime('%Y-%m-%d'),))
               booking_list = cursor.fetchall()
               matched_profiles.extend(booking_list)
               
            elif query.lower() in str(booking['price']):
               cursor.execute("SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                               JOIN locations ON workshops.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE workshops.price LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                               JOIN locations ON lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE lessons.price LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,one_on_one_lessons.lesson_name AS title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                               JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE one_on_one_lessons.price LIKE CONCAT('%', %s, '%');",(str(booking['price']),str(booking['price']),str(booking['price']),))
               booking_list = cursor.fetchall()
               matched_profiles.extend(booking_list)
            
            elif query.lower() in booking['user_name'].lower():
               cursor.execute("SELECT bookings.booking_id,workshops.title,workshops.date,workshops.start_time,workshops.end_time, workshops.price,workshops.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN workshops ON bookings.workshop_id = workshops.workshop_id\
                               JOIN locations ON workshops.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE member.user_name LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,lessons.title,lessons.date,lessons.start_time,lessons.end_time, lessons.price,lessons.capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN lessons ON bookings.lesson_id = lessons.lesson_id\
                               JOIN locations ON lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE member.user_name LIKE CONCAT('%', %s, '%')\
                               UNION\
                               SELECT bookings.booking_id,one_on_one_lessons.lesson_name AS title,one_on_one_lessons.date,one_on_one_lessons.start_time,one_on_one_lessons.end_time, one_on_one_lessons.price,1 AS capacity,locations.address,bookings.booking_type, member.user_name,member.first_name,member.last_name\
                               FROM bookings\
                               JOIN one_on_one_lessons ON bookings.one_on_one_id = one_on_one_lessons.lesson_id\
                               JOIN locations ON one_on_one_lessons.location_id = locations.location_id\
                               JOIN member ON member.member_id = bookings.user_id  WHERE member.user_name LIKE CONCAT('%', %s, '%');",(booking['user_name'],booking['user_name'],booking['user_name'],))
               booking_list = cursor.fetchall()
               matched_profiles.extend(booking_list)
        
        if not matched_profiles:
            flash('No matching bookings found.', 'info')
            return redirect(url_for('view_booking'))
        else:
            return render_template("booking/view_booking.html", booking_list=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))

@app.route('/booking_one_on_one/<int:course_id>')
def booking_one_on_one(course_id):
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        disabled = False
        msg = ''
        
        cursor.execute('SELECT * FROM bookings WHERE user_id = %s AND one_on_one_id = %s AND status = %s;',(session['id'], course_id,'Booked',))
        exist_bookings = cursor.fetchall()          
           
        cursor.execute('SELECT one_on_one_lessons.lesson_id as course_id,instructor.instructor_id,instructor.first_name as instr_first, instructor.last_name as instr_last,one_on_one_lessons.lesson_name, one_on_one_lessons.date, one_on_one_lessons.start_time,one_on_one_lessons.end_time,locations.name as location,locations.address\
                           FROM one_on_one_lessons \
                          JOIN instructor ON one_on_one_lessons.instructor_id = instructor.instructor_id\
                          JOIN locations ON locations.location_id = one_on_one_lessons.location_id\
                          WHERE one_on_one_lessons.lesson_id = %s;',(course_id,)) 
        course = cursor.fetchone()
           
        if course is None:
    
           return redirect(url_for('member_dashboard'))
        else:          
       
          cursor.fetchall()
          
          if exist_bookings:
              disabled = True
              msg = 'You have already booked this lesson'
              
              ool_query = """SELECT * FROM one_on_one_lessons 
                           WHERE instructor_id = %s AND status = 'Scheduled' 
                           ORDER BY date, start_time"""
                           
              cursor.execute(ool_query, (course['instructor_id'],))
              one_on_one_lessons_data = cursor.fetchall() 
              
              return render_template('member/member_view_1on1.html', 
                               one_on_one_lessons_data=one_on_one_lessons_data, 
                               role=session['role'],disabled = disabled, msg = msg)        
             
          else:
            cursor.execute('INSERT INTO bookings (user_id,one_on_one_id,booking_type,status) VALUES(%s,%s,%s,%s)',(session['id'],course['course_id'],'Lesson','Booked',))
            return redirect(url_for('member_pay_one_one_one_lesson',lesson_id = course['course_id']))       
                
    else:
        return redirect(url_for('login'))