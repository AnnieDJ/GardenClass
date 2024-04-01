from app import app
from flask import  render_template,flash
from flask import session,request, redirect,url_for
from app import utils

@app.route('/location/view_location')
def view_location():
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM locations;')
        location_list = cursor.fetchall()
        cursor.close()
        
        return render_template('/locations/location.html', location_list = location_list, role = session['role'])
    else:
         return redirect(url_for('login'))
     
@app.route('/location/manage_location/<int:location_id>',methods =['GET', 'POST'])
def manage_location(location_id):
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM locations WHERE location_id = %s;',(location_id,))
        location = cursor.fetchone()
        
        
        if request.method == 'POST':
           location_name = request.form.get('location_name')
           location_address = request.form.get('location_address')
           capacity = request.form.get('capacity')
           
           cursor = utils.getCursor()
           cursor.execute('UPDATE locations SET name = %s, address = %s, capacity = %s WHERE location_id = %s',(location_name,location_address,capacity,location_id,))
           cursor.close()
           
           return redirect(url_for('view_location'))
        else:
            return render_template('/locations/edit_location.html', location = location, role = session['role'])
    else:
         return redirect(url_for('login'))
     
@app.route('/location/delete_location/<int:location_id>',methods =['GET', 'POST'])
def delete_location(location_id):
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()
        cursor.execute('DELETE FROM locations WHERE location_id=%s',(location_id,))    
        cursor.close()
        
        return redirect(url_for('view_location'))
   
    else:
         return redirect(url_for('login'))
     
@app.route('/location/add_location',methods =['GET', 'POST'])
def add_location():
    if 'loggedin' in session and session['loggedin']:
        
        cursor = utils.getCursor()       
        
        if request.method == 'POST':
           location_name = request.form.get('location_name')
           location_address = request.form.get('location_address')
           capacity = request.form.get('capacity')
           
           cursor = utils.getCursor()
           cursor.execute('INSERT INTO locations (name, address,capacity) VALUES (%s, %s, %s)',(location_name, location_address,capacity,))
           cursor.close()
           
           return redirect(url_for('view_location'))
        else:
            return render_template('/locations/add_location.html', role = session['role'])
    else:
         return redirect(url_for('login'))
     
@app.route('/location_search')
def location_search():
    if 'loggedin' in session and session['loggedin']:
        query = request.args.get('search', '')
      
        cursor = utils.getCursor()
        cursor.execute('SELECT * FROM locations;')
        locations = cursor.fetchall()
        
        if query is None or query == '':
            return redirect(url_for('view_location'))
        
        matched_profiles = []
        for location in locations:
            if query.lower() in location['name'].lower():
               cursor.execute("SELECT * FROM locations WHERE name LIKE CONCAT('%', %s, '%');",(location['name'],))
               location_list = cursor.fetchall()
               matched_profiles.extend(location_list)
            
            elif query.lower() in location['address'].lower():
               cursor.execute("SELECT * FROM locations WHERE address LIKE CONCAT('%', %s, '%');",(location['address'],))
               location_list = cursor.fetchall()
               matched_profiles.extend(location_list)
            
            elif str(query).lower() in str(location['capacity']).lower():
                cursor.execute("SELECT * FROM locations WHERE capacity LIKE CONCAT('%', %s, '%');",(location['capacity'],))
                location_list = cursor.fetchall()
                matched_profiles.extend(location_list)
        
        if not matched_profiles:
            flash('No matching users found.', 'info')
            return redirect(url_for('view_location'))
        else:
            return render_template("locations/location.html", location_list=matched_profiles, role=session['role'])
    else:
         return redirect(url_for('login'))
