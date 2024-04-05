from app import app
from flask import render_template, redirect, url_for
from flask import session,request
from app import utils
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


@app.route('/payment/member_pay_one_one_one_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def member_pay_one_one_one_lesson(lesson_id):
    if 'loggedin' in session and session['loggedin']:
        msg = ''
        disable = False
        
        cursor = utils.getCursor()
        cursor.execute('SELECT one_on_one_lessons.lesson_name,one_on_one_lessons.status as lesson_status,one_on_one_lessons.price,bookings.status as booking_status \
                         FROM one_on_one_lessons \
                         JOIN bookings\
                         ON one_on_one_lessons.lesson_id = bookings.one_on_one_id\
                         WHERE one_on_one_lessons.lesson_id =%s;',(lesson_id,))
        one_on_one_lesson = cursor.fetchone()
        
        cursor.execute('SELECT * FROM bank_info WHERE member_id = %s;' ,(session['id'],))
        bank_info = cursor.fetchone()
        
        if one_on_one_lesson is not None and one_on_one_lesson['booking_status'] == 'Booked':
            if request.method == 'POST':
                bank_name = request.form.get('bank_name')
                bank_card = request.form.get('bank_card')
                security_code = request.form.get('security_code')
                
                payment_date = utils.current_date_time()
               
                cursor.execute('UPDATE bank_info SET bank_name = %s,security_code = %s, bank_card = %s WHERE member_id = %s',(bank_name,security_code,bank_card,session['id'],))
                cursor.execute('INSERT payments (user_id,amount,payment_type,payment_date,status) VALUES (%s,%s,%s,%s,%s)',(session['id'],one_on_one_lesson['price'],'Lesson',payment_date,'Completed'))
                return redirect(url_for('member_dashboard'))
            else:
             return render_template('/payment/pay_one_on_one_lesson.html', bank_info = bank_info, username=session['username'], role=session['role'])   
        
        else: 
            msg = 'There is no fee for this course.'
            disable = True  
            return render_template('/payment/pay_one_on_one_lesson.html', bank_info = bank_info, username=session['username'], role=session['role'])
    else:
      return redirect(url_for('login'))
    
@app.route('/payment/member_pay_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def member_pay_lesson(lesson_id):
   if 'loggedin' in session and session['loggedin']:
        msg = ''
        disable = False
        
        cursor = utils.getCursor()
        cursor.execute('SELECT lessons.title,lessons.price,bookings.status as booking_status \
                        FROM lessons \
                        JOIN bookings\
                        ON lessons.lesson_id = bookings.lesson_id\
                        WHERE lessons.lesson_id =%s;',(lesson_id,))
        lesson = cursor.fetchone()
        
        cursor.execute('SELECT * FROM bank_info WHERE member_id = %s;' , (session['id'],))
        bank_info = cursor.fetchone()
        
        if lesson is not None and lesson['booking_status'] == 'Booked':
            if request.method == 'POST':
                bank_name = request.form.get('bank_name')
                bank_card = request.form.get('bank_card')
                security_code = request.form.get('security_code')
                
                payment_date = utils.current_date_time()
               
                cursor.execute('UPDATE bank_info SET bank_name = %s, security_code = %s, bank_card = %s WHERE member_id = %s',(bank_name,security_code,bank_card,session['id'],))
                cursor.execute('INSERT payments (user_id,amount,payment_type,payment_date,status) VALUES (%s,%s,%s,%s,%s)',(session['id'],lesson['price'],'Lesson',payment_date,'Completed',))
                return redirect(url_for('member_dashboard'))
            else:
             return render_template('/payment/pay_lessons.html', bank_info = bank_info, username=session['username'], role=session['role'])   
        
        else: 
            msg = 'There is no fee for this course.'
            disable = True  
            return render_template('/payment/pay_lessons.html', bank_info = bank_info, username=session['username'], role=session['role'])
   else:
      return redirect(url_for('login'))
@app.route('/payment/member_pay_workshop/<int:workshop_id>', methods=['GET', 'POST'])
def member_pay_workshop(workshop_id):
    if 'loggedin' in session and session['loggedin']:
        msg = ''
        disable = False
        
        cursor = utils.getCursor()
        cursor.execute('SELECT workshops.title,workshops.price,bookings.status as booking_status \
                        FROM workshops \
                        JOIN bookings\
                        ON workshops.workshop_id = bookings.lesson_id\
                        WHERE workshops.workshop_id =%s;',(workshop_id,))
        workshop = cursor.fetchone()
        
        cursor.execute('SELECT * FROM bank_info WHERE member_id = %s;' , (session['id'],))
        bank_info = cursor.fetchone()
        
        if workshop is not None and workshop['booking_status'] == 'Booked':
            if request.method == 'POST':
                bank_name = request.form.get('bank_name')
                bank_card = request.form.get('bank_card')
                security_code = request.form.get('security_code')
                
                payment_date = utils.current_date_time()
               
                cursor.execute('UPDATE bank_info SET bank_name = %s, security_code = %s, bank_card = %s WHERE member_id = %s',(bank_name,security_code,bank_card,session['id'],))
                cursor.execute('INSERT payments (user_id,amount,payment_type,payment_date,status) VALUES (%s,%s,%s,%s,%s)',(session['id'],workshop['price'],'Workshop',payment_date,'Completed'))
                return redirect(url_for('member_dashboard'))
            else:
             return render_template('/payment/pay_workshop.html', bank_info = bank_info, username=session['username'], role=session['role'])   
        
        else: 
            msg = 'There is no fee for this course.'
            disable = True  
            return render_template('/payment/pay_workshop.html', bank_info = bank_info, username=session['username'], role=session['role'])
    else:
      return redirect(url_for('login'))
@app.route('/payment/member_pay_subscription', methods=['GET', 'POST'])
def member_pay_subscription():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('UPDATE subscriptions SET status = \'Expired\' WHERE user_id = %s AND CURRENT_DATE > end_date;',(session['id'],))
        cursor.execute('SELECT * FROM subscriptions WHERE CURDATE() BETWEEN start_date AND end_date AND user_id =%s;',(session['id'],))
        member_sub_item = cursor.fetchone()
        
        cursor.execute('SELECT * FROM subscriptions WHERE CURRENT_DATE > DATE_SUB(end_date, INTERVAL 10 DAY) AND CURRENT_DATE < end_date AND user_id = %s;',(session['id'],))
        can_pay_sub = cursor.fetchone()
        msg = ''
        disable = False
        
        if request.method == 'POST':
        
              pay_type = request.form.get('pay_type')
              
              if pay_type == 'Annual':
                #Annual pay, can change the amount as required
                pay_amount = 1000
                expiry_date = utils.one_year_later()
              else:
                  #Monthly Pay, can change the amount as required
                 pay_amount = 100
                 expiry_date_origin = utils.one_month_later()
                 expiry_date = datetime(expiry_date_origin.year, expiry_date_origin.month, expiry_date_origin.day)
                
              payment_date = utils.current_date_time()
              
              if member_sub_item is None or member_sub_item['status'] == 'Expired':
                   cursor.execute('INSERT INTO subscriptions (user_id, type, start_date, end_date, status) VALUES (%s, %s, %s, %s, %s);',(session['id'],pay_type,payment_date,expiry_date,'Active'))
                   cursor.execute('INSERT INTO payments (user_id,amount,payment_type,payment_date,status) VALUES (%s,%s,%s,%s,%s)',(session['id'],pay_amount,'Subscription',payment_date,'Completed'))
                   return redirect(url_for('member_dashboard'))
              elif can_pay_sub is not None:
                  if pay_type == 'Annual':
                     start_date = member_sub_item['end_date']
                     expiry_date = member_sub_item['end_date'] + relativedelta(months=12)
                  else:
                     start_date = member_sub_item['end_date']
                     expiry_date = member_sub_item['end_date'] + relativedelta(months=1)
                     
                  cursor.execute('UPDATE subscriptions SET end_date = %s, type = %s WHERE CURDATE() BETWEEN start_date AND end_date AND user_id =%s ;',(expiry_date,pay_type,session['id'],))
                  cursor.execute('INSERT INTO payments (user_id,amount,payment_type,payment_date,status) VALUES (%s,%s,%s,%s,%s)',(session['id'],pay_amount,'Subscription',payment_date,'Completed'))
                  return redirect(url_for('member_dashboard'))
              else:
                 msg ='There is no need to pay any amount.'
                 disable = True
                 return render_template('/payment/member_pay_sub.html', username=session['username'], role=session['role'],msg = msg, disable=disable)
        else:
            return render_template('/payment/member_pay_sub.html', username=session['username'], role=session['role'],msg = msg, disable=disable) 
        
        
    else:
       return redirect(url_for('login'))