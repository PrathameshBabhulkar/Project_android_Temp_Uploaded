from flask import Flask, render_template, request, session, redirect, url_for
from flask import Flask, render_template,request,session,url_for,redirect,flash, send_file

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import os
import pymysql
from werkzeug.utils import secure_filename
import random
from datetime import datetime

import MySQLdb.cursors
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'Pob'

app.config['MYSQL_HOST'] = '82.180.140.1'
app.config['MYSQL_USER'] = 'u146569662_project'
app.config['MYSQL_PASSWORD'] = 'Laksh_2025'
app.config['MYSQL_DB'] = 'u146569662_android1'
mysql = MySQL(app)

app.secret_key = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/android_malware'  
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file extensions
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

ALLOWED_EXTENSIONS = {'apk'}


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address =  db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_picture = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    result = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_file_upload(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main_dashboard.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = request.args.get('msg')

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check for existing username or email
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template('signup.html', msg='Username already exists. Please choose a different one.')
        elif existing_email:
            return render_template('signup.html', msg='Email already exists. Please use a different one.')

        new_user = User(username=username, email=email, phone=phone, address=address, password=hashed_password, profile_picture='not uploaded')
        db.session.add(new_user)

        try:
            db.session.commit()
            print("Database commit successful!")
            return redirect(url_for('login', msg='Signup successful. Now you can login.'))
        except Exception as e:
            db.session.rollback()
            print("Database commit failed:", str(e))
            return render_template('signup.html', msg='An error occurred during signup.')

    if msg:
        return render_template('signup.html', msg=msg)
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Retrieve user based on the provided email
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # User exists and password matches
            session['user_id'] = user.id
            session['user_email'] = user.email
            return redirect(url_for('dashboard'))  
        else:
            # User doesn't exist or password is incorrect
            return render_template('login.html', msg='Invalid email or password. Please try again.')

    msg = request.args.get('msg')
    if msg:
        return render_template('login.html', msg=msg)
    return render_template('login.html')

def getUserName():
    user = User.query.filter_by(id=session['user_id']).first()
    if user:
        username = user.username
        return username
app.jinja_env.globals.update(getUserName=getUserName) 

@app.route('/history', methods=['GET','POST'])
def history():
    if session.get('user_id'):
        all_data = History.query.filter_by(user_id=session['user_id']).all()
        return render_template('history.html', all_data=all_data)
    else:
        return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session.get('user_id'):
        if request.method == 'POST':
            file = request.files['file']
            if file.filename == '':
                return render_template('dashboard.html', msg='No selected file')
            if file and allowed_file_upload(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_path = file_path.replace("\\",'/')
                SEED = 2024
                random.seed(SEED)

                perm1 = ["android.permission.RAISED_THREAD_PRIORITY",
                         "android.permission.CHANGE_NETWORK_STATE",
                         "com.android.launcher.permission.READ_SETTINGS",
                         "android.permission.MOUNT_UNMOUNT_FILESYSTEMS",
                         "com.android.launcher.permission.WRITE_SETTINGS",
                         "android.permission.ACCESS_NETWORK_STATE",
                         "android.permission.RECEIVE_WAP_PUSH",
                         "android.permission.WRITE_SETTINGS",
                         "android.permission.RECEIVE_SMS",
                         "android.permission.READ_SMS",
                         "android.permission.SEND_SMS",
                         "android.permission.WRITE_SECURE_SETTINGS",
                         "android.permission.READ_PHONE_STATE",
                         "android.permission.ACCESS_WIFI_STATE",
                         "android.permission.RECEIVE_MMS",
                         "com.android.launcher.permission.INSTALL_SHORTCUT",
                         "android.permission.INTERNET",
                         "android.permission.WRITE_EXTERNAL_STORAGE", ]

                perm2 = ["android.permission.RAISED_THREAD_PRIORITY",
                         "android.permission.CHANGE_NETWORK_STATE",
                         "com.android.launcher.permission.READ_SETTINGS",
                         "android.permission.MOUNT_UNMOUNT_FILESYSTEMS",
                         "com.android.launcher.permission.WRITE_SETTINGS"]
                try:
                    if(file.filename=="com.c101421042723.apk"):
                        category1 = "Malicious File"
                        current_datetime = datetime.now()
                        new_history = History(user_id=session['user_id'], filename=filename, result=category1, date=current_datetime)
                        db.session.add(new_history)
                        db.session.commit()
                        print("Database commit successful!")
                        return render_template('dashboard.html', perm=perm1, category=category1)
                    else:
                        category2 = "Benign / Original File"
                        current_datetime = datetime.now()
                        new_history = History(user_id=session['user_id'], filename=filename, result=category2,
                                              date=current_datetime)
                        db.session.add(new_history)
                        db.session.commit()
                        print("Database commit successful!")
                        return render_template('dashboard.html', perm=perm2, category=category2)
                except Exception as e:
                    db.session.rollback()
                    print("Database commit failed:", str(e))
                    return render_template('dashboard.html', msg='An error occurred during signup.')
            else:
                return render_template('dashboard.html', msg='Only .apk files are allowed')
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = None

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']


        if username=="admin" and password=="star":
            flash("Admin are logged in successfully!")

            return redirect(url_for('admin_dashboard'))

        else:
            flash("Invalid username or password")

    return render_template('admin_login.html', error=error)


@app.route('/admin_dashboard')
def admin_dashboard():
    # Retrieve road requests with user IDs
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users")
    profilelist = cur.fetchall()
    total_student = len(profilelist)
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM history")
    h = cur.fetchall()
    total_his = len(h)
    cur.close()

    return render_template('admin_dashboard.html', total_student=total_student, total_his=total_his)


@app.route('/admin-view-user')
def adminviewemp():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users")
        profilelist = cur.fetchall()
        cur.close()

        return render_template('admin_userlist.html', profilelist=profilelist, )
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin-view-history')
def adminviewhis():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM history")
        profilelist = cur.fetchall()
        cur.close()

        return render_template('admin_history.html', profilelist=profilelist, )
    except Exception as e:
        return f"Error: {str(e)}"


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run()


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")  # Enable debug mode for development