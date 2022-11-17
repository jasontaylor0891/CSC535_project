import os
import sys
import json

from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_wtf import FlaskForm
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from forms import ChangePasswordForm, RegistrationForm, LoginForm, CreateList, CreateProfile, updateUserProfile
from userservices import UserService
from reminderservice import ReminderService
from functools import wraps
from datetime import datetime


app = Flask(__name__, template_folder='templates')

if app.config['ENV'] == "production":
	print(f'Type: Production', file=sys.stderr)
	app.config.from_object("config.ProductionConfig")
elif app.config['ENV'] == "development":
	print(f'Type: Development', file=sys.stderr)
	app.config.from_object("config.DevelopmentConfig")
else:
	print(f'Type: Testing', file=sys.stderr)
	app.config.from_object("config.TestingConfig")

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
	#UserService.login()
	#print(app.config)
	print(f'{app.config}', file=sys.stderr)
	return render_template("home.html"); 

#Login route.  This function logs the user into the application and determins their account profile
#and redirect the user to their appropriate dashboard.
@app.route('/login', methods = ['GET', 'POST'])
def login():
	
	form = LoginForm(request.form)
	# if request.method == 'GET':
	# 		form.username.data = username

	if request.method == 'POST' and form.validate():
		username = request.form['username']
		password_candidate = request.form['password']

		responce = UserService.login(username, password_candidate)
		if responce:
			content = json.loads(responce)

			if content['Auth'] == 'True':
				session['logged_in'] = True
				session['username'] = content['username']
				session['profile'] = content['profile']
				return redirect(url_for('main_app', username = content['username']))
			else:
				errorcode = content['errorcode']
				if errorcode == '001':
					error = 'The username and password you entered did not match our records.  Please double check and try again.'
				if errorcode == '002': 
					error = 'Your username was not found in our records. Please double check and try again.'
				if errorcode == '007': 
					error = 'Your account has been locked. Please contact the administrator.'
				return render_template('login.html', form = form, error = error)

	return render_template('login.html', form = form)

#Route and Function for adminDashboard
@app.route('/main_app', methods = ['GET', 'POST'])
@is_logged_in
def main_app():

	responce = ReminderService.displayReminders()

	if responce:
		content = json.loads(responce)

		if content['Auth'] == 'True':
			return render_template("main.html", data=content['data'], success="true")  
					
		else:
			errorcode = content['errorcode']
			if errorcode == '002': 
				error = 'No reminders to display. Please double check and try again.'
			return render_template('main.html', error = error)
	
	return render_template("main.html")


#Route and function for changing user password
@app.route('/update_password/<string:username>', methods = ['GET', 'POST'])
@is_logged_in
def update_password(username):
	
	form = ChangePasswordForm(request.form)
	if request.method == 'POST' and form.validate():
		new = form.new_password.data
		entered = form.old_password.data

		responce = UserService.updatepassword(username, entered, new)
		print(f'Updated: {responce}', file=sys.stderr)
		if responce:
			content = json.loads(responce)
			
			if content['Updated'] == 'True':
				flash('Your new password will be in effect from next login!!', 'info')
				return redirect(url_for('profile', username = session['username']))
			else:
				errorcode = content['errorcode']
				if errorcode == '003':
					error = 'Your current password you entered did not match our records. Please double check and try again.'
					return render_template('updatePassword.html', form = form, error = error)

	return render_template('updatePassword.html', form = form)

#Route and Function for logout function
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

#Route and function for the registration page
@app.route('/registration/', methods=["GET","POST"])
def registration():
	
	try:
		session['logged_in'] = False

		form = RegistrationForm(request.form)
		if request.method == 'POST':
			fname = form.fname.data
			lname = form.lname.data
			username = form.username.data
			email = form.email.data
			password = form.password.data
			mtype = form.mtype.data
			phone = form.phone.data
				
			responce = UserService.registration(fname, lname, username, email, password, mtype, phone)
			print(f'Call Responce: {responce}', file=sys.stderr)
			if responce:
				content = json.loads(responce)
				if content['Success'] == 'True':
					flash(f'The user {username} was sucessfuly created.')
					return redirect(url_for('login'))
				else:
					errorcode = content['errorcode']
					if errorcode == '004':
						error = 'There was an issue during the registration process. Please contact the administrator if the problem continues.'
						return render_template("registration.html", form=form, error=error)

		return render_template("registration.html", form=form)
	
	except Exception as e:
		return(str(e))

list = []
#I know we should be able to have this CreateReminder class in forms.py.  
#I was not able to figure out how to send username to the class.
#We can refactor this later.  Just adding this here to move the 
#project forward until we figure out how to make this work from forms.py
class CreateReminder(Form):
	priority = []
	priority.clear()
	priority.append("None")
	priority.append("High")
	priority.append("Medium")
	priority.append("Low")

	ReminderName = StringField('Reminder Name:', [validators.Length(min=1, max=50)])
	ReminderMessage = StringField('Message:', [validators.Length(min=1, max=5000)])
	ReminderStartDate = DateField('Start Date (DD-MM-YYYY)', format='%d-%m-%Y')
	priority = SelectField('Priority:', choices = priority)
	list = SelectField('List:', choices = list)

#Route and function for the create reminder page
@app.route('/create_reminder/', methods=["GET","POST"])
@is_logged_in
def create_reminder():
	try:
		username = session['username']
		list.clear()

		#Create the list for the membership types
		cur = mysql.connection.cursor()
		q = cur.execute('SELECT listname FROM list WHERE username = %s', [username])
		b = cur.fetchall()
		for i in range(q):
			list.append(b[i]['listname'])

		form = CreateReminder(request.form)
		
		if request.method == 'POST':
			remindername = form.ReminderName.data
			remindermessage = form.ReminderMessage.data
			reminderstartdate = request.form['ReminderStartDate']
			#reminderstartdate = form.ReminderStartDate.data
			priority = form.priority.data
			reminderlist = form.list.data
			username = session['username']

			responce = ReminderService.createreminder(remindername, remindermessage, reminderstartdate, priority, reminderlist, username)
			print(f'Call Responce: {responce}', file=sys.stderr)
			if responce:
				content = json.loads(responce)
				if content['Success'] == 'True':
					flash(f'The reminder {remindername} was sucessfuly created.')
					return redirect(url_for('main_app', username = session['username']))
				else:
					errorcode = content['errorcode']
					if errorcode == '006':
						error = 'There was an issue creating your reminder.  Please contact the administrator if the problem continues.'
						return render_template("create_reminder.html", form=form, error=error)

		return render_template("create_reminder.html", form=form)
	except Exception as e:
		return(str(e))

#Route and function for the create reminder page
@app.route('/createlist/', methods=["GET","POST"])
@is_logged_in
@is_paid_tie
def createlist():
	try:
		form = CreateList(request.form)
		if request.method == 'POST':
			listname = form.listname.data
			listdesc = form.listdesc.data
			username = session['username']
			responce = ReminderService.createlist(listname, listdesc, username)
			print(f'Call Responce: {responce}', file=sys.stderr)
			if responce:
				content = json.loads(responce)
				if content['Success'] == 'True':
					flash(f'The list {listname} was sucessfuly created.')
					return redirect(url_for('main_app', username = session['username']))
				else:
					errorcode = content['errorcode']
					if errorcode == '005':
						error = 'There was an issue when creating your list. Please contact the administrator if the problem continues.'
						return render_template("createlist.html", form=form, error=error)


		return render_template("createlist.html", form=form)
	except Exception as e:
		return(str(e))

#Route and function for the create reminder page
@app.route('/profile/', methods=["GET","POST"])
@is_logged_in
def profile():
	try:
		form = CreateProfile(request.form)
		#if request.method == 'POST':
			


		return render_template("profile.html", form=form)
	except Exception as e:
		return(str(e))


#Route and function for the User Profile
@app.route('/userProfile/', methods=["GET","POST"])
def userProfile():
	
	try:
		print('Inside the userProfile try function', file=sys.stderr)
		username = session['username']

		cur = mysql.connection.cursor()
		query = cur.execute('SELECT fname, lname, username, email, phone FROM users WHERE username = %s', [username])
		print(query, file=sys.stderr)
		results = cur.fetchone()
		print(results, file=sys.stderr)
		#results.keys()

		query_fname = results["fname"]
		query_lname = results["lname"]
		query_username = results["username"]
		query_email = results["email"]
		query_phone = results["phone"]

		print(query_fname, query_lname, query_username, query_email, query_phone, file=sys.stderr)
		print("THESE ARE THE RESULTS", file=sys.stderr)
		
		form = updateUserProfile(request.form)
		
		if request.method == 'GET':
			form.fname.data = query_fname
			form.lname.data = query_lname
			form.username.data = query_username
			form.email.data = query_email
			form.phone.data = query_phone

			return render_template("userProfile.html", form=form)

		elif request.method == 'POST':
			fname = form.fname.data
			lname = form.lname.data
			new_username = form.username.data
			email = form.email.data
			phone = form.phone.data
			mtype = form.mtype.data
			
			response = UserService.updateUserInformation(fname, lname, new_username, email, mtype, phone, query_username)
			print(f'Call Responce: {response}', file=sys.stderr)
			if response:
				content = json.loads(response)
				if content['Success'] == 'True':
					flash(f'The user {username} had the profile updated')
					return redirect(url_for('login'))
				else:
					errorcode = content['errorcode']
					if errorcode == '004':
						error = 'Errori in updating user information.'
						return render_template("userProfile.html", form=form, error=error)

		return render_template("userProfile.html", form=form)
	
	except Exception as e:
		return(str(e))

@app.route('/deleteReminder/<int:reminderId>', methods=['GET', 'POST'])
@is_logged_in
def deleteReminder(reminderId):
	print('MADE IT INSIDE DELETE REMINDER FUNCTION', file=sys.stderr)
	print(reminderId, file=sys.stderr)
	#Delete the reminder
	delete_Reminder = ReminderService.deleteReminder(reminderId)
	if delete_Reminder:
		content = json.loads(delete_Reminder)
		if content['Success'] == 'True':
				flash(f'The reminder was sucessfuly deleted!')
				return redirect(url_for('main_app', username = session['username']))
		else:
			errorcode = content['errorcode']
			if errorcode == '006':
				error = 'There was an issue deleting your reminder.'
				return render_template("main_app.html")
						
    			#return redirect(url_for('main_app'))