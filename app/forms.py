from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_wtf import FlaskForm
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo


#Form for changing user password
class ChangePasswordForm(Form):
	old_password = PasswordField('Existing Password')
	new_password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords do not match!')
	])
	confirm = PasswordField('Confirm Password')