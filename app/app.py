from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_wtf import FlaskForm
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from forms import ChangePasswordForm

from functools import wraps
from datetime import datetime


app = Flask(__name__, template_folder='templates')
app.secret_key = "welcome123"

#Change mysql host if not using docker. Docker default is gym_managment_db_1
app.config['MYSQL_HOST'] = 'CSC535_project_db_1'
app.config['MYSQL_USER'] = 'csc535'
app.config['MYSQL_PASSWORD'] = 'welcome123'
app.config['MYSQL_DB'] = 'csc535'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

#function to determine if logged in to application.
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('You are not logged in.  Please Login :)', 'danger')
			return redirect(url_for('login'))
	return wrap

#function to determin if the logged in user using the free tier.
def is_free_tier(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] == 3:
			return f(*args, **kwargs)
	return wrap

#function to determin if the logged in user using the paid tier.
def is_paid_tie(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] == 2:
			return f(*args, **kwargs)
		else:
			flash('You do not have access to the paid tier, You do not have access to this page.', 'danger')
			return redirect(url_for('login'))
	return wrap

#function to determin if the logged in user is a administrator.
def is_admin(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] == 1:
			return f(*args, **kwargs)
		else:
			flash('You are not an admin!!, No access to this page.', 'danger')
			return redirect(url_for('login'))
	return wrap

#default route to the applications homepage
@app.route('/')
def index():
    return render_template("home.html"); 

#Login route.  This function logs the user into the application and determins their account profile
#and redirect the user to their appropriate dashboard.
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM logins WHERE username = %s', [username])
        if result>0:
            data = cur.fetchone()
            cur.close()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['profile'] = data['profile']
                flash('You are logged in', 'success')
                
				#return redirect(url_for('main', username = username))
                return redirect(url_for('main_app', username = username))
				
            else:
                error = 'Invalid login'
                return render_template('login.html', error = error)

		
        else:
            error = 'Username NOT FOUND'
            return render_template('login.html', error = error)

    return render_template('login.html')

#Route and Function for adminDashboard
@app.route('/main_app')
@is_logged_in
def main_app():
    return render_template("main.html");


#Route and function for changing user password
@app.route('/update_password/<string:username>', methods = ['GET', 'POST'])
def update_password(username):
	
	form = ChangePasswordForm(request.form)
	if request.method == 'POST' and form.validate():
		new = form.new_password.data
		entered = form.old_password.data

		#getting current password from the database
		cur = mysql.connection.cursor()
		cur.execute("SELECT password FROM logins WHERE username = %s", [username])
		old = (cur.fetchone())['password']

		#IF the old password entered matches the db then update db with the new password
		if sha256_crypt.verify(entered, old):
			cur.execute("UPDATE logins SET password = %s WHERE username = %s", (sha256_crypt.encrypt(new), username))
			mysql.connection.commit()
			cur.close()
			flash('New password will be in effect from next login!!', 'info')
			return redirect(url_for('memberDashboard', username = session['username']))
		
		cur.close()
		flash('Old password you entered is not correct!!, try again', 'warning')

	return render_template('updatePassword.html', form = form)

#Route and Function for logout function
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))


app.run(host="0.0.0.0", port=int("8000"), debug=True)
