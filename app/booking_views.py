from app import app
from app import utils
from flask import Flask, render_template, jsonify
import json
import datetime


#Showing the calendar
@app.route('/courses')
def get_courses():
    return  render_template('/booking/booking_lessons.html')

#getting courses and make a booking
@app.route('/get_course_info')
def get_course_info():
    cursor = utils.getCursor()
    cursor.execute('SELECT instructor.first_name as instr_first, instructor.last_name as instr_last,lessons.title, lessons.date, lessons.start_time,lessons.end_time \
                    FROM lessons \
                    JOIN instructor ON lessons.instructor_id = instructor.instructor_id;')
    courses = cursor.fetchall()
    course_data = []
    for course in courses:
        start_time = datetime.datetime.combine(course['date'], datetime.datetime.min.time()) + course['start_time']
        end_time = datetime.datetime.combine(course['date'], datetime.datetime.min.time()) + course['end_time']
        
        title = course['title'] + ' ' + course['instr_first'] + ' ' + course['instr_last'] + ' Lessons'
        course_data.append({
             'title': title,  
             'start': start_time.isoformat(),  
             'end': end_time.isoformat()
        })
              
    return jsonify(course_data)
