from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'jjhjhjh'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pdc'

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
        if request.method == 'POST' and 'id1' in request.form and 'id2' in request.form and'id3' in request.form and'id4' in request.form and'id5' in request.form and'id6' in request.form and 'id7' in request.form and 'id8' in request.form:
            sem1 = request.form['id1']
            sem2 = request.form['id2']
            sem3 = request.form['id3']
            sem4 = request.form['id4']
            sem5 = request.form['id5']
            sem6 = request.form['id6']
            sem7 = request.form['id7']
            sem8 = request.form['id8']
            username=session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
            #account = cursor.fetchone()
            cursor.execute('SELECT * from academics where uid=%s',(username,))
            if cursor.rowcount==0:
                cursor.execute('INSERT into academics(uid,id1,id2,id3,id4,id5,id6,id7,id8) values (%s,%s, %s,%s,%s,%s,%s,%s,%s)', (username,sem1,sem2,sem3,sem4,sem5,sem6,sem7,sem8))
                mysql.connection.commit()
            elif cursor.rowcount!=0:
                sql_update_query = """Update academics set id1=%s,id2=%s,id3=%s,id4=%s,id5=%s,id6=%s,id7=%s,id8=%s where uid = %s"""
                inputData = (sem1,sem2,sem3,sem4,sem5,sem6,sem7,sem8,username)
                cursor.execute(sql_update_query, inputData)
                mysql.connection.commit()
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
    cursor.execute('INSERT into project(uid, title, mentor, domain, outcome, abstract) values (3, %s,%s, %s,%s,%s)', (title, mentor, domain, outcome, abstract))
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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT into miniproject values (3, %s,%s, %s,%s,%s)', (title, mentor, domain, outcome, abstract))
    mysql.connection.commit()
   
    return render_template('table-row.html', a = title,
        b = mentor,
        c = domain,
        d = outcome,
        e = abstract)



@app.route('/rpaper', methods=['GET', 'POST'])
def rpaper():
    msg=''
    if 'loggedin' in session:
        if request.method == 'POST':
           return redirect(url_for('patent')) 

    return render_template('rpaper.html',msg=msg)

@app.route('/api/rpaper', methods=['GET', 'POST'])
def api_research():
    title = request.form.get('title')
    mentor = request.form.get('mentor')
    domain = request.form.get('domain')
    outcome = request.form.get('outcome')
    abstract = request.form.get('abstract')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT into research values (3, %s,%s, %s,%s,%s)', (title, mentor, domain, outcome, abstract))
    mysql.connection.commit()
   
    return render_template('table-row.html', a = title,
        b = mentor,
        c = domain,
        d = outcome,
        e = abstract)


@app.route('/patent', methods=['GET', 'POST'])
def patent():
    msg=''
    if 'loggedin' in session:
        if request.method == 'POST':
           return redirect(url_for('co')) 

    return render_template('patent.html',msg=msg)

@app.route('/api/patent', methods=['GET', 'POST'])
def api_patent():
    title = request.form.get('title')
    mentor = request.form.get('mentor')
    domain = request.form.get('domain')
    outcome = request.form.get('outcome')
    abstract = request.form.get('abstract')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT into patent values (3, %s,%s, %s,%s,%s)', (title, mentor, domain, outcome, abstract))
    mysql.connection.commit()
   
    return render_template('table-row.html', a = title,
        b = mentor,
        c = domain,
        d = outcome,
        e = abstract)



@app.route('/co', methods=['GET', 'POST'])
def co():
    msg=''
    if 'loggedin' in session:
        if request.method == 'POST':
           return redirect(url_for('extra')) 

    return render_template('co.html',msg=msg)

@app.route('/extra', methods=['GET', 'POST'])
def extra():
    msg=''
    if 'loggedin' in session:
        if request.method == 'POST':
           return redirect(url_for('social')) 

    return render_template('extra.html',msg=msg)   

@app.route('/social', methods=['GET', 'POST'])
def social():
    msg=''
    return render_template('social.html',msg=msg)    
   


if __name__ =='__main__':
    app.run(debug=True)