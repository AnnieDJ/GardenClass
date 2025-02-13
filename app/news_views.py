from app import app
from flask import  render_template,flash
from flask import session,request, redirect,url_for
from app import utils

# view news
@app.route('/news/view_news')
def view_news():
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM news;')

        news_list = cursor.fetchall()
        
        return render_template('/news/news.html', news_list = news_list, role = session['role'])
    else:
         return redirect(url_for('login'))

# manage news     
@app.route('/news/manage_news/<int:news_id>', methods=['GET', 'POST'])
def manage_news(news_id):
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM news WHERE news_id = %s;', (news_id,))
        news = cursor.fetchone()

        if request.method == 'POST':
            news_title = request.form.get('title')
            news_content = request.form.get('content')
            date_published = request.form.get('date_published')

            cursor = utils.getCursor()
            cursor.execute('UPDATE news SET title = %s, content = %s, date_published = %s WHERE news_id = %s', (news_title, news_content, date_published, news_id))
            cursor.close()

            return redirect(url_for('view_news'))
        else:
            return render_template('/news/edit_news.html', news=news, role=session['role'])
    else:
        return redirect(url_for('login'))

# delete news    
@app.route('/news/delete_news/<int:news_id>',methods =['GET', 'POST'])
def delete_news(news_id):
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM news WHERE news_id=%s',(news_id,))    
        cursor.close()
        
        return redirect(url_for('view_news'))
   
    else:
         return redirect(url_for('login'))
    
 
# add news    
@app.route('/news/add_news', methods=['GET', 'POST'])
def add_news():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()       

        if request.method == 'POST':
            user_id = session.get('id')
            news_title = request.form.get('title')
            news_content = request.form.get('content')
            date_published = request.form.get('date_published')
            author_id = user_id  # Assuming user_id is the correct identifier for the author
            
            cursor.execute('INSERT INTO news (user_id,title, content, date_published, author_id) VALUES (%s,%s, %s, %s, %s)', (user_id,news_title, news_content, date_published, author_id))
            cursor.close()
            flash('Add News successfully!', 'success')
            return redirect(url_for('view_news'))
            
        else:
            return render_template('/news/add_news.html', role=session['role'])
    else:
        return redirect(url_for('login'))

# news search
@app.route('/news_search')
def news_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM news;')
        news = cursor.fetchall()
        
        if query is None or query == '':
            return redirect(url_for('view_news'))
        
        matched_profiles = []
        for new in news:
            if query.lower() in new['title'].lower():
               cursor.execute("SELECT * FROM news WHERE title LIKE CONCAT('%', %s, '%');",(new['title'],))
               news_list = cursor.fetchall()
               matched_profiles.extend(news_list)
            
            elif query.lower() in new['content'].lower():
               cursor.execute("SELECT * FROM news WHERE content LIKE CONCAT('%', %s, '%');", (new['content'],))
               news_list = cursor.fetchall()
               matched_profiles.extend(news_list)
            
            elif str(query).lower() in str(new['date_published']).lower():
                cursor.execute("SELECT * FROM news WHERE date_published LIKE CONCAT('%', %s, '%');",(new['date_published'],))
                news_list = cursor.fetchall()
                matched_profiles.extend(news_list)
        
        if not matched_profiles:
            flash('No matching users found.', 'info')
            return redirect(url_for('view_news'))
        else:
            return render_template("news/news.html", news_list=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))

# member view news
@app.route('/member_view_news')
def member_view_news():
    if 'loggedin' in session and session['loggedin']:
        cursor = utils.getCursor()
        
        title = request.args.get('title')
        date = request.args.get('date')
        
        sql_query = """
        SELECT n.news_id, n.title, n.content, n.date_published, 
                COALESCE(m.first_name, 'system') AS first_name, COALESCE(m.last_name, 'system') AS last_name
        FROM news n
        LEFT JOIN manager m ON n.author_id = m.manager_id
        WHERE 1=1
        """

        query_params = []
        
        sql_query += " AND user_id is null OR user_id = %s"
        query_params.append(session['id'])
        
        if title:
            sql_query += " AND n.title LIKE %s"
            query_params.append(f"%{title}%")
        if date:
            sql_query += " AND DATE(n.date_published) = %s"
            query_params.append(date)
        
        sql_query += " ORDER BY n.date_published DESC"
        
        cursor.execute(sql_query, query_params)
        news_articles = cursor.fetchall()
        return render_template('member/member_view_news.html', news_articles=news_articles)
        
    else: 
        return redirect(url_for('login'))  # make sure to redirect to the correct login route