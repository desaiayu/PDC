from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import pathlib


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'jjhjhjh'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pdcc'
app.config['FILES'] = './Files/'
# app.config['ACADEMICS'] = './Files/Academics/'
app.config['COC'] = './Files/CoC/'
# app.config['EXTRAC'] = './Files/ExtraC/'
# app.config['SOCIAL'] = './Files/Social/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    msg = ''
    session.clear()
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg='')
    


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

    

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    
    
    return redirect(url_for('login'))    


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    msg=''
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from project where uid like %s', (session['username'],))
        if cursor.rowcount != 0:
            msg = cursor.fetchone()
        if request.method == 'POST' and 'id1' in request.form and 'id2' in request.form and'id3' in request.form and'id4' in request.form and'id5' in request.form and'id6' in request.form and 'id7' in request.form and 'id8' in request.form:
            marksheet = request.files['file'] 
            if marksheet and marksheet.filename != '' and '.' in marksheet.filename and marksheet.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                extension = '.' + marksheet.filename.rsplit('.', 1)[1].lower()
                sem1 = request.form['id1']
                sem2 = request.form['id2']
                sem3 = request.form['id3']
                sem4 = request.form['id4']
                sem5 = request.form['id5']
                sem6 = request.form['id6']
                sem7 = request.form['id7']
                sem8 = request.form['id8']
                username=session['username']
                msg = marksheet.filename
                # os.rename(app.config['ACADEMICS'] + marksheet.filename, app.config['ACADEMICS'] + session['username'] + extension)
                cursor.execute('SELECT * from academics where uid=%s',(username,))
                if cursor.rowcount==0:
                    cursor.execute('INSERT into academics(uid,id1,id2,id3,id4,id5,id6,id7,id8, marksheet) values (%s,%s, %s,%s,%s,%s,%s,%s,%s,%s)', (username,sem1,sem2,sem3,sem4,sem5,sem6,sem7,sem8,app.config['FILES']+session['username']+'/Academics/'+marksheet.filename))
                    mysql.connection.commit()
                elif cursor.rowcount!=0:
                    os.remove((cursor.fetchone())['marksheet'])
                    sql_update_query = """Update academics set id1=%s,id2=%s,id3=%s,id4=%s,id5=%s,id6=%s,id7=%s,id8=%s,marksheet=%s  where uid = %s"""
                    inputData = (sem1,sem2,sem3,sem4,sem5,sem6,sem7,sem8,app.config['FILES']+session['username']+'/Academics/'+marksheet.filename,username)
                    cursor.execute(sql_update_query, inputData)
                    mysql.connection.commit()
                pathlib.Path(app.config['FILES'], session['username']).mkdir(exist_ok=True)
                pathlib.Path(app.config['FILES'], session['username']+'/Academics/').mkdir(exist_ok=True)
                marksheet.save(os.path.join(app.config['FILES'], session['username']+'/Academics/', marksheet.filename))
                return redirect(url_for('finyear'))
        elif request.method == 'POST':
        # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
    
        return render_template('profile.html',msg=msg)
    
    return redirect(url_for('login')) 



@app.route('/finyear', methods=['GET', 'POST'])
def finyear():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from project where uid like %s', (session['username'],))
        msg = session['username']
        if cursor.rowcount != 0:
            msg = cursor.fetchall()
        if request.method == 'POST':
           return redirect(url_for('mini')) 
        return render_template('finyear.html',msg=msg)
    return redirect(url_for('login'))  

@app.route('/api/finyear', methods=['GET', 'POST'])
def api_project():
    title = request.form.get('title')
    mentor = request.form.get('mentor')
    domain = request.form.get('domain')
    outcome = request.form.get('outcome')
    abstract = request.form.get('abstract')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    username=session['username']
    cursor.execute('INSERT into project(uid, title, mentor, domain, outcome, abstract) values (%s, %s,%s, %s,%s,%s)', (username,title, mentor, domain, outcome, abstract))
    mysql.connection.commit()
    last_id = cursor.lastrowid
    print(last_id)
   
    return render_template('table-row.html', a = title,
        b = mentor,
        c = domain,
        d = outcome,
        e = abstract,
        f = last_id)

@app.route('/api/finyear/delete', methods=['POST'])
def del_project():
    a = request.form.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE from project where id = %s", [a])
    mysql.connection.commit()
    
    return 'True'


@app.route('/mini', methods=['GET', 'POST'])
def mini():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from miniproject where uid like %s', (session['username'],))
        msg = session['username']
        if cursor.rowcount != 0:
            msg = cursor.fetchall()
        if request.method == 'POST':
           return redirect(url_for('rpaper')) 
        return render_template('mini.html',msg=msg)
    return redirect(url_for('login'))    

@app.route('/api/mini', methods=['GET', 'POST'])
def api_mini():
    title = request.form.get('title')
    mentor = request.form.get('mentor')
    domain = request.form.get('domain')
    outcome = request.form.get('outcome')
    abstract = request.form.get('abstract')
    username=session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT into miniproject (uid, title, mentor, domain, outcome, abstract) values (%s, %s,%s, %s,%s,%s)', (username,title, mentor, domain, outcome, abstract))
    mysql.connection.commit()
    last_id = cursor.lastrowid
    print(last_id)
   
    return render_template('table-row.html', a = title,
        b = mentor,
        c = domain,
        d = outcome,
        e = abstract,
        f = last_id)

@app.route('/api/mini/delete', methods=['POST'])
def del_miniproject():
    a = request.form.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE from miniproject where id = %s", [a])
    mysql.connection.commit()
    
    return 'True'


@app.route('/rpaper', methods=['GET', 'POST'])
def rpaper():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from research where uid like %s', (session['username'],))
        msg = session['username']
        if cursor.rowcount != 0:
            msg = cursor.fetchall()
            for item in msg:
                item['acceptance_letter'] = (item['acceptance_letter'].rsplit('/'))[-1]
        if request.method == 'POST':
           return redirect(url_for('patent')) 
        return render_template('rpaper.html',msg=msg)
    return redirect(url_for('login')) 

@app.route('/api/rpaper', methods=['GET', 'POST'])
def api_research():
    Project_Title = request.form.get('Project_Title')
    Name_of_the_mentor = request.form.get('Name_of_the_mentor')
    Domain = request.form.get('Domain')
    Outcome = request.form.get('Outcome')
    Abstract = request.form.get('Abstract')
    Name_of_Publisher = request.form.get('Name_of_Publisher')
    certi = request.files.get('file')
    username=session['username']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    Certificate = certi.filename
    if certi and Certificate != '' and '.' in Certificate and Certificate.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        pathlib.Path(app.config['FILES'], session['username']).mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Research/').mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Research/'+Project_Title+'/').mkdir(exist_ok=True)
        certi.save(os.path.join(app.config['FILES'], session['username']+'/Research/'+Project_Title+'/', Certificate))
    cursor.execute('INSERT into research (uid, title, mentor, domain, outcome, abstract,publisher,acceptance_letter)  values (%s, %s,%s, %s,%s,%s,%s,%s)', (username,Project_Title, Name_of_the_mentor, Domain, Outcome, Abstract,Name_of_Publisher,app.config['FILES']+session['username']+'/Research/'+Project_Title+'/'+Certificate))
    mysql.connection.commit()
    last_id = cursor.lastrowid
    print(last_id)
   
    return render_template('table-row2.html', a = Project_Title,
        b = Name_of_the_mentor,
        c = Domain,
        d = Outcome,
        e = Abstract,
        f = Name_of_Publisher,
        g = Certificate,
        h = last_id
        )

@app.route('/api/rpaper/delete', methods=['POST'])
def del_rpaper():
    a = request.form.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from research where id = %s", [a])
    folder = cursor.fetchone()
    os.remove(folder['acceptance_letter'])
    os.rmdir('./Files/'+session['username']+'/Research/'+folder['title'])
    cursor.execute("DELETE from research where id = %s", [a])
    mysql.connection.commit()
    
    return 'True'

@app.route('/patent', methods=['GET', 'POST'])
def patent():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from patent where uid like %s', (session['username'],))
        msg = session['username']
        if cursor.rowcount != 0:
            msg = cursor.fetchall()
            for item in msg:
                item['acceptance_letter'] = (item['acceptance_letter'].rsplit('/'))[-1]
        if request.method == 'POST':
           return redirect(url_for('co')) 
        return render_template('patent.html',msg=msg)
    return redirect(url_for('login')) 

@app.route('/api/patent', methods=['GET', 'POST'])
def api_patent():
    Project_Title = request.form.get('Project_Title')
    Name_of_the_mentor = request.form.get('Name_of_the_mentor')
    Domain = request.form.get('Domain')
    Outcome = request.form.get('Outcome')
    Abstract = request.form.get('Abstract')
    Status = request.form.get('Status')
    certi = request.files.get('file')
    username=session['username']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    Certificate = certi.filename
    if certi and Certificate != '' and '.' in Certificate and Certificate.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        # extension = '.' + Certificate.rsplit('.', 1)[1].lower()
        pathlib.Path(app.config['FILES'], session['username']).mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Patent/').mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Patent/'+Project_Title+'/').mkdir(exist_ok=True)
        certi.save(os.path.join(app.config['FILES'], session['username']+'/Patent/'+Project_Title+'/', Certificate))
    cursor.execute('INSERT into patent (uid, title, mentor, domain, outcome, abstract,status,acceptance_letter)  values (%s, %s,%s, %s,%s,%s,%s,%s)', (username,Project_Title, Name_of_the_mentor, Domain, Outcome, Abstract,Status,app.config['FILES']+session['username']+'/Patent/'+Project_Title+'/'+Certificate))
    mysql.connection.commit()
    last_id = cursor.lastrowid
    print(last_id)
   
    return render_template('table-row2.html', a = Project_Title,
        b = Name_of_the_mentor,
        c = Domain,
        d = Outcome,
        e = Abstract,
        f = Status,
        g = Certificate,
        h = last_id
        )

@app.route('/api/patent/delete', methods=['POST'])
def del_patent():
    a = request.form.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from patent where id = %s", [a])
    folder = cursor.fetchone()
    os.remove(folder['acceptance_letter'])
    os.rmdir('./Files/'+session['username']+'/Patent/'+folder['title'])
    cursor.execute("DELETE from patent where id = %s", [a])
    mysql.connection.commit()
    
    return 'True'

@app.route('/co', methods=['GET', 'POST'])
def co():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from cocirricular where uid like %s', (session['username'],))
        msg = session['username']
        if cursor.rowcount != 0:
            msg = cursor.fetchall()
            for item in msg:
                item['certificate'] = (item['certificate'].rsplit('/'))[-1]
        if request.method == 'POST':
           return redirect(url_for('extra')) 
        return render_template('co.html',msg=msg)
    return redirect(url_for('login')) 

@app.route('/api/co', methods=['GET', 'POST'])
def api_co():
    
    Name_of_activity = request.form.get('Name_of_activity')
    Location = request.form.get('Location')
    Type_of_activity =request.form.get('Type_of_activity')
    Date_of_activity = request.form.get('Date_of_activity')
    Awards = request.form.get('Awards')
    Cash_Prize = request.form.get('Cash_Prize')
    certi= request.files.get('file')
    username=session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    Certificate = certi.filename
    if certi and Certificate != '' and '.' in Certificate and Certificate.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        pathlib.Path(app.config['FILES'], session['username']).mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Co Curricular/').mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Co Curricular/'+Name_of_activity+'/').mkdir(exist_ok=True)
        certi.save(os.path.join(app.config['FILES'], session['username']+'/Co Curricular/'+Name_of_activity+'/', Certificate))
    cursor.execute('INSERT into cocirricular (uid,name,date,type,award,location,cash_prize,certificate) values (%s, %s,%s, %s,%s,%s,%s,%s)', (username,Name_of_activity,Date_of_activity,Type_of_activity,Awards,Location,Cash_Prize,app.config['FILES']+session['username']+'/Co Curricular/'+Name_of_activity+'/'+Certificate))
    mysql.connection.commit()
    last_id = cursor.lastrowid
    print(last_id)
    
   
    return render_template('table-row2.html', a = Name_of_activity,
        b = Date_of_activity,
        c = Type_of_activity,
        d = Awards,
        e = Location,
        f = Cash_Prize,
        g = Certificate,
        h = last_id
        )

@app.route('/api/co/delete', methods=['POST'])
def del_co():
    a = request.form.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from cocirricular where id = %s", [a])
    folder = cursor.fetchone()
    os.remove(folder['certificate'])
    os.rmdir('./Files/'+session['username']+'/Co Curricular/'+folder['name'])
    cursor.execute("DELETE from cocirricular where id = %s", [a])
    mysql.connection.commit()
    
    return 'True'

@app.route('/extra', methods=['GET', 'POST'])
def extra():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from extracirricular where uid like %s', (session['username'],))
        msg = session['username']
        if cursor.rowcount != 0:
            msg = cursor.fetchall()
            for item in msg:
                item['certificate'] = (item['certificate'].rsplit('/'))[-1]
        if request.method == 'POST':
           return redirect(url_for('social')) 
        return render_template('extra.html',msg=msg) 
    return redirect(url_for('login'))   

@app.route('/api/extra', methods=['GET', 'POST'])
def api_extra():
    Name_of_activity = request.form.get('Name_of_activity')
    Location = request.form.get('Location')
    Type_of_activity =request.form.get('Type_of_activity')
    Date_of_activity = request.form.get('Date_of_activity')
    Awards = request.form.get('Awards')
    Cash_Prize = request.form.get('Cash_Prize')
    certi= request.files.get('file')
    username=session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    Certificate = certi.filename
    if certi and Certificate != '' and '.' in Certificate and Certificate.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        pathlib.Path(app.config['FILES'], session['username']).mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Extra Curricular/').mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Extra Curricular/'+Name_of_activity+'/').mkdir(exist_ok=True)
        certi.save(os.path.join(app.config['FILES'], session['username']+'/Extra Curricular/'+Name_of_activity+'/', Certificate))
        
    cursor.execute('INSERT into extracirricular (uid,name,date,type,award,location,cash_prize,certificate) values (%s, %s,%s, %s,%s,%s,%s,%s)', (username,Name_of_activity,Date_of_activity,Type_of_activity,Awards,Location,Cash_Prize,app.config['FILES']+session['username']+'/Extra Curricular/'+Name_of_activity+'/'+Certificate))
    mysql.connection.commit()
    last_id = cursor.lastrowid
    print(last_id)
    
   
    return render_template('table-row2.html', a = Name_of_activity,
        b = Date_of_activity,
        c = Type_of_activity,
        d = Awards,
        e = Location,
        f = Cash_Prize,
        g = Certificate,
        h = last_id
        )

@app.route('/api/extra/delete', methods=['POST'])
def del_extra():
    a = request.form.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from extracirricular where id = %s", [a])
    folder = cursor.fetchone()
    os.remove(folder['certificate'])
    os.rmdir('./Files/'+session['username']+'/Extra Curricular/'+folder['name'])
    cursor.execute("DELETE from extracirricular where id = %s", [a])
    mysql.connection.commit()
    
    return 'True'

@app.route('/social', methods=['GET', 'POST'])
def social():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from social where uid like %s', (session['username'],))
        msg = session['username']
        if cursor.rowcount != 0:
            msg = cursor.fetchall()
            for item in msg:
                item['certificate'] = (item['certificate'].rsplit('/'))[-1]
        return render_template('social.html',msg=msg) 
    return redirect(url_for('login'))    
   
@app.route('/api/social', methods=['GET', 'POST'])
def api_social():
    Name_of_activity = request.form.get('Name_of_activity')
    Date_of_activity = request.form.get('Date_of_activity')
    Type_of_activity = request.form.get('Type_of_activity')
    Duration = request.form.get('Duration')
    certi= request.files.get('file')
    username=session['username']

    Certificate = certi.filename
    if certi and Certificate != '' and '.' in Certificate and Certificate.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        pathlib.Path(app.config['FILES'], session['username']).mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Social/').mkdir(exist_ok=True)
        pathlib.Path(app.config['FILES'], session['username']+'/Social/'+Name_of_activity+'/').mkdir(exist_ok=True)
        certi.save(os.path.join(app.config['FILES'], session['username']+'/Social/'+Name_of_activity+'/', Certificate))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT into social(uid,name,date,duration,nature,certificate) values (%s, %s,%s, %s,%s,%s)', (username,Name_of_activity,Date_of_activity,Duration,Type_of_activity,app.config['FILES']+session['username']+'/Social/'+Name_of_activity+'/'+Certificate))
    mysql.connection.commit()
    last_id = cursor.lastrowid
    print(last_id)
   
    return render_template('table-row.html', a = Name_of_activity,
        b = Date_of_activity,
        c = Duration,
        d = Type_of_activity,
        e = Certificate,
        f = last_id)

@app.route('/api/social/delete', methods=['POST'])
def del_social():
    a = request.form.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from social where id = %s", [a])
    folder = cursor.fetchone()
    os.remove(folder['certificate'])
    os.rmdir('./Files/'+session['username']+'/Social/'+folder['name'])
    cursor.execute("DELETE from social where id = %s", [a])
    mysql.connection.commit()
    
    return 'True'

if __name__ =='__main__':
    app.run(debug=True)