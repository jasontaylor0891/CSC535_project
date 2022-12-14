import os
import sys
import json

from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_wtf import FlaskForm
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField, SubmitField, DateField, widgets, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from sqlescapy import sqlescape

from forms import ChangePasswordForm, RegistrationForm, LoginForm, CreateList, CreateProfile, updateUserProfile
from userservices import UserService
from reminderservice import ReminderService
from functools import wraps
from datetime import datetime, date
from utility import *


app = Flask(__name__, template_folder='templates')

if app.config['ENV'] == "production":
	logging.debug(f'Type: Production')
	app.config.from_object("config.ProductionConfig")
elif app.config['ENV'] == "development":
	logging.debug(f'Type: Development')
	app.config.from_object("config.DevelopmentConfig")
else:
	logging.debug(f'Type: Testing')
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

	logging.debug(f'{app.config}')
	return render_template("home.html"); 

#Login route.  This function logs the user into the application and determins their account profile
#and redirect the user to their appropriate dashboard.
@app.route('/login', methods = ['GET', 'POST'])
def login():
	
	form = LoginForm(request.form)
	# if request.method == 'GET':
	# 		form.username.data = username

	if request.method == 'POST' and form.validate():
		username = sqlescape(request.form['username'])
		password_candidate = sqlescape(request.form['password'])

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
		new = sqlescape(form.new_password.data)
		entered = sqlescape(form.old_password.data)

		responce = UserService.updatepassword(username, entered, new)
		logging.debug(f'Updated: {responce}')
		
		if responce:
			content = json.loads(responce)
			
			if content['Updated'] == 'True':
				flash('Your new password will be in effect from next login!!', 'info')
				return redirect(url_for('profile', username = session['username']))
			else:
				errorcode = content['errorcode']
				if errorcode == '003':
					error = 'Your current password you entered did not match our records. Please double check and try again.'
				if errorcode == '008':
						error = 'Tne new password does not meet length or complexity requirements. (minimum length 12 characters, 2 uppercase characters, 2 numeric characters, and 2 special characters.)'
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
			fname = sqlescape(form.fname.data)
			lname = sqlescape(form.lname.data)
			username = sqlescape(form.username.data)
			email = sqlescape(form.email.data)
			password = sqlescape(form.password.data)
			mtype = form.mtype.data
			phone = sqlescape(form.phone.data)
				
			responce = UserService.registration(fname, lname, username, email, password, mtype, phone)
			logging.debug(f'Call Responce: {responce}')
			
			if responce:
				content = json.loads(responce)
				if content['Success'] == 'True':
					flash(f'The user {username} was sucessfuly created.', 'info')
					return redirect(url_for('login'))
				else:
					errorcode = content['errorcode']
					if errorcode == '004':
						error = 'There was an issue during the registration process. Please contact the administrator if the problem continues.'
					if errorcode == '008':
						error = 'Password does not meet length or complexity requirements. (minimum length 12 characters, 2 uppercase characters, 2 numeric characters, and 2 special characters.)'
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
	ReminderStartDate = DateField('Start Date (MM/DD/YYYY)', [DataRequired()], format='%Y-%m-%d')
	priority = SelectField('Priority:', choices = priority)
	list = SelectField('List:', choices = list)
	flag = BooleanField('Flag this reminder?', default=False)

	def validate_ReminderStartDate(form, field):
		todaysdate = date.today()
		logging.debug(f"Todays Date: {todaysdate}")

		rdate = datetime.strptime(field.raw_data[0], '%Y-%m-%d').date()
		logging.debug(f"Input Date: {rdate}")

		if rdate < todaysdate:
			logging.info(f"Validation Result: False - Input Date is past date")
			field.errors.append("Start Date cannot be in the past!")
			return False
		else:
			logging.info(f"Validation Result: True - Input Date is not past date")
			return True
	

#Route and function for the create reminder page
@app.route('/create_reminder/', methods=["GET","POST"])
@is_logged_in
def create_reminder():
	logging.info("In create reminder")
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
		
		if request.method == 'POST' and form.validate():
			remindername = sqlescape(form.ReminderName.data)
			remindermessage = sqlescape(form.ReminderMessage.data)
			reminderstartdate = sqlescape(request.form['ReminderStartDate'])
			#reminderstartdate = form.ReminderStartDate.data
			priority = form.priority.data
			reminderlist = form.list.data
			username = session['username']
			flag = form.flag.data

			responce = ReminderService.createreminder(remindername, remindermessage, reminderstartdate, priority, reminderlist, username, flag)
			logging.debug(f'Call Responce: {responce}')
			
			if responce:
				content = json.loads(responce)
				if content['Success'] == 'True':
					flash(f'The reminder {remindername} was sucessfuly created.', 'info')
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
			listname = sqlescape(form.listname.data)
			listdesc = sqlescape(form.listdesc.data)
			username = session['username']
			responce = ReminderService.createlist(listname, listdesc, username)
			logging.debug(f'Call Responce: {responce}')
			
			if responce:
				content = json.loads(responce)
				if content['Success'] == 'True':
					flash(f'The list {listname} was sucessfuly created.', 'info')
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

	username = session['username']
	try:
		responce = UserService.display_user(username)
		if responce:
			content = json.loads(responce)
			
			if content['Success'] == 'True':
				return render_template("profile.html", data=content['data'], success="true")

		#return render_template("profile.html")
	except Exception as e:
		return(str(e))


#Route and function for the User Profile
@app.route('/userProfile/', methods=["GET","POST"])
@is_logged_in
def userProfile():
	
	try:
		
		logging.info('Inside the userProfile try function')
		username = session['username']

		cur = mysql.connection.cursor()
		query = cur.execute('SELECT fname, lname, username, email, phone FROM users WHERE username = %s', [username])
		logging.debug(f'{query}')
		results = cur.fetchone()
		logging.debug(f'{results}')
		#results.keys()

		query_fname = results["fname"]
		query_lname = results["lname"]
		query_username = results["username"]
		query_email = results["email"]
		query_phone = results["phone"]

		logging.debug(f'{query_fname}, {query_lname}, {query_username}, {query_email}, {query_phone}')
		logging.debug('THESE ARE THE RESULTS')
		
		form = updateUserProfile(request.form)
		
		if request.method == 'GET':
			form.fname.data = query_fname
			form.lname.data = query_lname
			form.username.data = query_username
			form.email.data = query_email
			form.phone.data = query_phone

			return render_template("userProfile.html", form=form)

		elif request.method == 'POST':
			fname = sqlescape(form.fname.data)
			lname = sqlescape(form.lname.data)
			new_username = sqlescape(form.username.data)
			email = sqlescape(form.email.data)
			phone = sqlescape(form.phone.data)
			mtype = form.mtype.data
			
			response = UserService.updateUserInformation(fname, lname, new_username, email, mtype, phone, query_username)
			logging.debug(f'Call Responce: {response}')
			
			if response:
				content = json.loads(response)
				if content['Success'] == 'True':
					flash(f'The user {username} had the profile updated', 'info')
					return redirect(url_for('profile'))
				else:
					errorcode = content['errorcode']
					if errorcode == '004':
						error = 'Errori in updating user information.'
						return render_template("userProfile.html", form=form, error=error)

		return render_template("userProfile.html", form=form)
	
	except Exception as e:
		return(str(e))

@app.route('/deleteReminder/<int:reminderId>/<deleteReminderMessage>', methods=['GET', 'POST'])
@is_logged_in
def deleteReminder(reminderId, deleteReminderMessage):
	logging.debug('MADE IT INSIDE DELETE REMINDER FUNCTION')
	logging.debug(f'{reminderId}')
	
	if deleteReminderMessage == 'displayMessage':
		responce = ReminderService.displayReminderToDelete(reminderId)
		content = json.loads(responce)
		logging.debug(f'Display Message: {content}')
		
		return render_template("main.html", data=content['data'], success="true", displayDeleteConfirmation="true")
	elif deleteReminderMessage == 'deleteTheReminder':
		
		delete_Reminder = ReminderService.deleteReminder(reminderId)
		if delete_Reminder:
			content = json.loads(delete_Reminder)
			if content['Success'] == 'True':
					flash(f'The reminder was sucessfuly deleted!', 'info')
					return redirect(url_for('main_app', username = session['username']))
			else:
				errorcode = content['errorcode']
				if errorcode == '006':
					error = 'There was an issue deleting your reminder.'
					return render_template("main_app.html")
							
					#return redirect(url_for('main_app'))

class filterReminder(Form):
	filterStartDate = DateField('Start Date (MM-DD-YYYY)', format='%d-%m-%Y')
	filterEndDate = DateField('End Date (MM-DD-YYYY)', format='%d-%m-%Y')

#Route and Function for adminDashboard
@app.route('/mainWithFilter', methods = ['GET', 'POST'])
@is_logged_in
def mainWithFilter():
	form = filterReminder(request.form)
	responce = ReminderService.displayReminders()

	if responce:
		content = json.loads(responce)

		if content['Auth'] == 'True':  
			if request.method == 'POST':
				filterStartDate1 = request.form['filterStartDate']
				filterEndDate1 = request.form['filterEndDate']
				logging.debug(f'FStartdate1: {filterStartDate1}')
				logging.debug(f'FEnddate1: {filterEndDate1}')
				
				if not filterStartDate1 or not filterEndDate1:
					flash('You need to enter BOTH a start and end date! Still displaying all reminders!', 'danger')
					return redirect(url_for('mainWithFilter'))
				elif filterStartDate1 > filterEndDate1:
					flash('Start date must be before end date! Still dislaying all reminders!', 'danger')
					return redirect(url_for('mainWithFilter'))
				
				logging.debug('PAST THE NULL CHECK!')
				responseFilter = ReminderService.filterTheReminder(filterStartDate1,filterEndDate1)
				newContent = json.loads(responseFilter)
				
				logging.debug(f'New Content: {newContent}')
				if newContent['Success'] == 'True':
					return render_template("mainWithFilter.html", data=newContent['data'], success="true", form = form)
				else:	
					flash('No reminders were found in this date range!', 'danger')
					#return redirect(url_for('mainWithFilter'))
					return render_template("mainWithFilter.html", data=newContent['data'], success="false", form = form)	
			return render_template("mainWithFilter.html", data=content['data'], success="true", form = form)
		else:
			errorcode = content['errorcode']
			if errorcode == '006':
				error = 'There was an issue deleting your reminder.'
				return render_template("mainWithFilter.html", data=content['data'], success="true", form = form)
			else:
				return render_template("mainWithFilter.html", data=content['data'], success="true", form = form)

	else:
		errorcode = content['errorcode']
		if errorcode == '002': 
			error = 'No reminders to display. Please double check and try again.'
			return render_template('mainWithFilter.html', error = error, form = form)

	return render_template("mainWithFilter.html", form = form)


# Not sure how to pass 'list' choices to forms.py so adding this class here
list_for_edit = []
class edit_Reminder(Form):
	priority = []
	priority.clear()
	priority.append("None")
	priority.append("High")
	priority.append("Medium")
	priority.append("Low")

	reminderName = StringField('Reminder Name:', [validators.Length(min=1, max=50)])
	reminderMessage = StringField('Message:', [validators.Length(min=1, max=5000)])
	reminderStartDate = DateField('Start Date (MM/DD/YYYY)', [DataRequired()], format='%Y-%m-%d')
	priority = SelectField('Priority:', choices = priority)
	list = SelectField('List:', choices = list_for_edit)
	flag = BooleanField('Flag this reminder?', default=False)

	def validate_reminderStartDate(form, field):
		todaysdate = date.today()
		logging.debug(f"Todays Date: {todaysdate}")

		rdate = datetime.strptime(field.raw_data[0], '%Y-%m-%d').date()
		logging.debug(f"Input Date: {rdate}")

		if rdate < todaysdate:
			logging.info(f"Validation Result: False - Input Date is past date")
			field.errors.append("Start Date cannot be in the past!")
			return False
		else:
			logging.info(f"Validation Result: True - Input Date is not past date")
			return True

#Route and function for edit reminder
@app.route('/editReminder/<int:reminderId>', methods=["GET","POST"])
@is_logged_in
def editReminder(reminderId):
	
	try:
		logging.info(f'Inside editReminder function')
		logging.debug(f'Reminder ID: {reminderId}')

		username = session['username']
		list_for_edit.clear()

		#Fetch reminder details of the reminder selected by user
		cur = mysql.connection.cursor()
		query = cur.execute( 'SELECT remindername, reminderdesc, priority, reminderstartdate, flaged, username, listid FROM reminders WHERE username = %s and reminderid = %s ', [username,reminderId])
		
		logging.debug(f'SQL {query}')
		results = cur.fetchone()
		logging.debug(f'Results: {results}')
		
		#Fetch list details of the user
		list_dict = {}
		q = cur.execute('SELECT listid, listname FROM list WHERE username = %s', [username])
		b = cur.fetchall()
		for i in range(q):
			list_for_edit.append(b[i]['listname'])
			list_dict[b[i]['listid']] = b[i]['listname']
		
		logging.debug(f'List: {list_dict}')

		query_remindername = results["remindername"]
		query_reminderdesc = results["reminderdesc"]
		query_priority = results["priority"]
		query_reminderstartdate = results["reminderstartdate"]
		flagged = results["flaged"]
		listName = list_dict[results["listid"]]
		
		logging.debug('Reminder results from DB:')
		logging.debug(f'{query_remindername}, {query_reminderdesc}, {query_priority}, {query_reminderstartdate}, {flagged}, {listName}')
		
		form = edit_Reminder(request.form)
		
		if request.method == 'GET':
			
			logging.debug('GET request')
			form.reminderName.data = query_remindername
			form.reminderMessage.data = query_reminderdesc
			form.priority.data = query_priority
			form.list.data = listName
			#date field
			form.reminderStartDate.raw_data = [str(query_reminderstartdate)]
			form.reminderStartDate.process_data(query_reminderstartdate)

			#checkbox
			if flagged == 1:
				form.flag.data = True
			else:
				form.flag.data = False

			return render_template("edit_reminder.html", form=form)
		
		elif request.method == 'POST' and form.validate():
			
			logging.debug('POST request')
			rem_name = sqlescape(form.reminderName.data)
			rem_desc = sqlescape(form.reminderMessage.data) 
			rem_priority = form.priority.data
			rem_list = form.list.data
			rem_flagged = form.flag.data
			#rem_startdate = form.reminderStartDate.data
			rem_startdate = request.form['reminderStartDate']

			logging.debug(f'Reminder details passed to Reminder service for edit:')
			logging.debug(f'{rem_name}, {rem_desc}, {rem_priority}, {rem_list}, {rem_startdate}, {rem_flagged}, {username}, {reminderId}')

			response = ReminderService.editreminder(rem_name, rem_desc, rem_priority, rem_list, rem_startdate, rem_flagged, username, reminderId)
			logging.debug(f'Edit reminder call response: {response}')

			if response:
				content = json.loads(response)

				if content['Success'] == 'True':
					flash(f'Reminder {rem_name} was sucessfuly updated.', 'info')
					return redirect(url_for('main_app', username = session['username'])) 
				else:
					errorcode = content['errorcode']
					if errorcode == '009':
						flash('Error in updating reminder. Please try again later.', 'danger')
						return redirect(url_for('main_app', username = session['username']))
			
		return render_template("edit_reminder.html", form=form)
		
	except Exception as e:
		logging.error(f'{str(e)}')
		return(str(e))