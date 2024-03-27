from app import app
from flask import render_template, redirect, url_for
from flask import session,request
from app import utils
from datetime import datetime


@app.route('/payment/member_pay_one_one_one_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def member_pay_one_one_one_lesson(lesson_id):
    if 'loggedin' in session and session['loggedin']:
        return render_template('/payment/pay_one_on_one_lesson.html', username=session['username'], role=session['role'])
    
@app.route('/payment/member_pay_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def member_pay_lesson(lesson_id):
    if 'loggedin' in session and session['loggedin']:
        return render_template('/payment/pay_lessons.html', username=session['username'], role=session['role'])
    
@app.route('/payment/member_pay_workshop/<int:workshop_id>', methods=['GET', 'POST'])
def member_pay_workshop(workshop_id):
    if 'loggedin' in session and session['loggedin']:
        return render_template('/payment/pay_workshop.html', username=session['username'], role=session['role'])
    
@app.route('/payment/member_pay_subscription', methods=['GET', 'POST'])
def member_pay_subscription():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM subscriptions WHERE CURDATE() BETWEEN start_date AND end_date AND user_id =%s;',(session['id'],))
        member_sub_item = cursor.fetchone()
        msg = ''
        disable = False
        
        if member_sub_item is None or member_sub_item['status'] == 'Expired':
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
              
              cursor.execute('INSERT INTO subscriptions (user_id, type, start_date, end_date, status) VALUES (%s, %s, %s, %s, %s);',(session['id'],pay_type,payment_date,expiry_date,'Active'))
              cursor.execute('INSERT INTO payments (user_id,amount,payment_type,payment_date,status) VALUES (%s,%s,%s,%s,%s)',(session['id'],pay_amount,'Subscription',payment_date,'Completed'))
              return redirect(url_for('member_dashboard'))
           else:
               return render_template('/payment/member_pay_sub.html', username=session['username'], role=session['role'],msg = msg, disable=disable) 
        else:
            msg ='There is no need to pay any amount.'
            disable = True
            return render_template('/payment/member_pay_sub.html', username=session['username'], role=session['role'],msg = msg, disable=disable)
    else:
      return redirect(url_for('login'))