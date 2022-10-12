from crypt import methods
import json
import sys
from flask import Flask, make_response, request, jsonify
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

app = Flask(__name__)


#Change mysql host if not using docker. Docker default is gym_managment_db_1
app.config['MYSQL_HOST'] = 'user_dbase'
app.config['MYSQL_USER'] = 'csc535'
app.config['MYSQL_PASSWORD'] = 'welcome123'
app.config['MYSQL_DB'] = 'csc535'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)


@app.route('/')
def index():
	cur = mysql.connection.cursor()
    #result = cur.execute('SELECT * FROM logins WHERE username = admin')
	
	select_stmt = "SELECT * FROM logins WHERE username = %(emp_no)s"
	result = cur.execute(select_stmt, { 'emp_no': "admin" })
	
	if result>0:
		data = cur.fetchone()
		cur.close()

	return jsonify(data)

@app.route('/user/login/', methods=['POST'])
def post_login():
	#print('Login function', file=sys.stderr)
	username = request.form['username']
	password_candidate = request.form['password']

	# print(f'Password Candidate: {password_candidate}', file=sys.stderr)
	cur = mysql.connection.cursor()
	result = cur.execute('SELECT * FROM logins WHERE username = %s', [username])

	if result>0:
		data = cur.fetchone()
		cur.close()
		password = data['password']

		# print(f'Password from DB: {password}', file=sys.stderr)

		# message = make_response(jsonify({'message': 'Logged in', 'profile':  data['profile']}))
		# print(f'Return: {message}', file=sys.stderr)

		if sha256_crypt.verify(password_candidate, data['password']):
			return make_response(jsonify({'Auth': 'True', 'profile':  data['profile'], 'username': data['username']}))
		
		return make_response(jsonify({'message': 'Not logged in'}), 401)

app.run()