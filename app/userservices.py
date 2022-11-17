#User-service
import sys
import json
import datetime

from flask_mysqldb import MySQL
from flask import Flask, make_response, request, jsonify
from passlib.hash import sha256_crypt

mysql = MySQL()

class UserService:
    def __init__(self):
        print('init called', file=sys.stderr)

    def login(username, password_candidate):
        print(f'User {username} login attempt started', file=sys.stderr)
        login_attempt = 0

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT loginAttempt, accountEnabled FROM users WHERE username = %s", [username])
        data = cur.fetchone()
        login_attempt = data['loginAttempt']
        account_enabled = data['accountEnabled']

        if account_enabled:
            print(f'Login Attempts: {login_attempt}', file=sys.stderr)
            if login_attempt == 2:
                result = cur.execute("UPDATE users SET accountEnabled = False WHERE username = %s", [username])
                mysql.connection.commit()
                cur.close()
                return json.dumps({'Auth': 'False','errorcode': '007'})

            
            result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

            if result == 0:
                cur.close()
                print(f'User {username} not found. 401 Not Authorized', file=sys.stderr)
                return json.dumps({'Auth': 'False','errorcode': '002'})

            if result>0:
                data = cur.fetchone()
                password = data['password']

                if sha256_crypt.verify(password_candidate, data['password']):
                    cur.execute("UPDATE users SET loginAttempt = 0 WHERE username = %s", [username])
                    mysql.connection.commit()
                    cur.close()
                    return json.dumps({'Auth': 'True', 'profile':  data['profile'], 'username': data['username']})
                else:
                    login_attempt = login_attempt + 1
                    result = cur.execute("UPDATE users SET loginAttempt = %s WHERE username = %s", [str(login_attempt), username])
                    mysql.connection.commit()
                    cur.close()
                    print(f'User {username} login failed. 401 Not Authorized', file=sys.stderr)
                    return json.dumps({'Auth': 'False','errorcode': '001'})

        else:
            cur.close()
            return json.dumps({'Auth': 'False','errorcode': '007'})

    def registration(fname, lname, username, email, password, mtype, phone):
        print(f'Registration process has started', file=sys.stderr)

        if mtype == "Free":
            profile = 3
        else:
            profile = 2
        
        accountcreated = str(datetime.date.today())

        try:
            
            #Insert user info into users table
            hash = sha256_crypt.hash(password)
            cur = mysql.connection.cursor()
            sql = ("INSERT INTO users(fname, lname, username, email, "
                "password, phone, profile, accountEnabled, accountCreated, totpEnabled)"
                "VALUES( '" +fname+ "', '" +lname+ "', '" +username+ "', "
                "'" +email+"', '"+hash+"', '"+phone+"', "+str(profile)+", True, '"+accountcreated+"', False)"
                )

            print(f'SQL Output {sql}', file=sys.stderr)
            results = cur.execute(sql)
            mysql.connection.commit()

            #Create default list
            sql = ("INSERT INTO list (listname, listdesc, username) "
            "VALUES('Default', 'Default List', '" +username+ "')")
            
            print(f'SQL Output {sql}', file=sys.stderr)
            results = cur.execute(sql)
            mysql.connection.commit()

            return json.dumps({'Success': 'True'})

        except Exception as e:
            print(f'{datetime.datetime.now()} Error: {str(e)}', file=sys.stderr)
            return json.dumps({'Success': 'False','errorcode': '004'})

        

    def updatepassword(username, oldpassword, newpassword):
        
        print(f'User {username} has started password change', file=sys.stderr)
        
        #getting current password from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", [username])
        old = (cur.fetchone())['password']

        #IF the old password entered matches the db then update db with the new password
        if sha256_crypt.verify(oldpassword, old):
            cur.execute("UPDATE users SET password = %s WHERE username = %s", (sha256_crypt.encrypt(newpassword), username))
            mysql.connection.commit()
            cur.close()
            return json.dumps({'Updated': 'True'})
        else:
            cur.close()
            return json.dumps({'Updated': 'False', 'errorcode': '003'})
    
    def updateUserInformation(fname, lname, new_username, email, mtype, phone, query_username):
        print(f'Update user information process has started', file=sys.stderr)

        if mtype == "Free":
            profile = 3
        else:
            profile = 2

        try:
            
            #Update user account information
            cur = mysql.connection.cursor()
            sql = ("UPDATE users "
                    "SET fname = '"+ fname + "', lname = '" +lname+ "', username = '" +new_username+ "', email = '" +email+"', phone = '" +phone+ "', profile = '"+str(profile)+"'"
                    " WHERE username = '" + query_username + "'")


            print(f'SQL Output {sql}', file=sys.stderr)
            results = cur.execute(sql)
            mysql.connection.commit()

            #update the list username field 
            sql = ("UPDATE list " 
                    "SET username = '" +new_username + "'"
                    " WHERE username = '"+query_username + "'"
            )
            
            print(f'SQL Output {sql}', file=sys.stderr)
            results = cur.execute(sql)
            mysql.connection.commit()

            #update the reminder username field 
            sql = ("UPDATE reminders " 
                    "SET username = '" +new_username + "'"
                    " WHERE username = '"+query_username + "'"
            )
            
            print(f'SQL Output {sql}', file=sys.stderr)
            results = cur.execute(sql)
            mysql.connection.commit()

            return json.dumps({'Success': 'True'})

        except Exception as e:
            print(f'{datetime.datetime.now()} Error: {str(e)}', file=sys.stderr)
            return json.dumps({'Success': 'False','errorcode': '004'})




