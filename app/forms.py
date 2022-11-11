from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_wtf import FlaskForm
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo




#Form for changing user password
class ChangePasswordForm(Form):
	old_password = PasswordField('Existing Password:')
	new_password = PasswordField('New Password:', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords do not match!')
	])
	confirm = PasswordField('Confirm Password:')

class RegistrationForm(Form):
	membershipType = []
	membershipType.clear()
	membershipType.append("Free")
	membershipType.append("Paid")

	fname = StringField('First Name:', [validators.Length(min=3, max=20)])
	lname = StringField('Last Name:', [validators.Length(min=3, max=20)])
	username = StringField('Username:', [validators.Length(min=6, max=20)])
	email = StringField('Email Address:', [validators.Length(min=6, max=50)])
	password = PasswordField('Password:', [
        validators.InputRequired(),
        validators.EqualTo('confirm:', message='Passwords must match')
    ])
	confirm = PasswordField('Confirm Password:')
	mtype = SelectField('Membership Type:', choices = membershipType)
	phone = StringField('Phone Number:', [validators.Length(min=10, max=10)])
	
class LoginForm(Form):
	username = StringField('Username:', [validators.DataRequired()])
	password = PasswordField('Password:', [validators.DataRequired()])

class CreateProfile(Form):
	pass

# class CreateReminder(Form):
# 	priority = []
# 	priority.clear()
# 	priority.append("None")
# 	priority.append("High")
# 	priority.append("Medium")
# 	priority.append("Low")


# 	ReminderName = StringField('Reminder Name:', [validators.Length(min=1, max=50)])
# 	ReminderMessage = StringField('Message:', [validators.Length(min=1, max=5000)])
# 	ReminderStartDate = DateField('Start Date (DD-MM-YYYY)', format='%d-%m-%Y')
# 	priority = SelectField('Priority:', choices = priority)
# 	list = SelectField('List:', choices = list)
	

class CreateList(Form):

	listname = StringField('List Name:', [validators.Length(max=50)])
	listdesc = StringField('List Description:', [validators.Length(max=250)])


class updateUserProfile(Form):
	membershipType = []
	membershipType.clear()
	membershipType.append("Free")
	membershipType.append("Paid")

	fname = StringField('First Name:', [validators.Length(min=3, max=20)])
	lname = StringField('Last Name:', [validators.Length(min=3, max=20)])
	username = StringField('Username:', [validators.Length(min=6, max=20)])
	email = StringField('Email Address:', [validators.Length(min=6, max=50)])
	mtype = SelectField('Membership Type:', choices = membershipType)
	phone = StringField('Phone Number:', [validators.Length(min=10, max=10)])