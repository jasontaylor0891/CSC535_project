import sys
import json
import datetime

from flask_mysqldb import MySQL
from flask import current_app, session

mysql = MySQL()

class ReminderService:
    
    
    def createlist(listname, listdesc, username):

        config = current_app.config
        print(f'{config}', file=sys.stderr)
        
        print(f'Create list process has started', file=sys.stdout)

        try:
            
            cur = mysql.connection.cursor()

            sql = ("INSERT INTO list (listname, listdesc, username) "
            "VALUES('" +listname+ "', '" +listdesc+ "', '" +username+ "')")

            print(f'SQL Output {sql}', file=sys.stderr)
            results = cur.execute(sql)
            mysql.connection.commit()

            return json.dumps({'Success': 'True'})

        except Exception as e:
            print(f'{datetime.datetime.now()} Error: {str(e)}', file=sys.stderr)
            return json.dumps({'Success': 'False','errorcode': '005'})

    
    def displayReminders():
        username = session['username']
        print(f'Displaying reminders for user {username}', file=sys.stderr)

        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM reminders WHERE username = %s', [username])
       
        if result == 0:
            cur.close()
            print(f'User {username} not found. 401 Not Authorized', file=sys.stderr)
            return json.dumps({'Auth': 'False','errorcode': '002'})

        if result>0:
            data = cur.fetchall()
            cur.close()
        
        return json.dumps({'Auth': 'True', 'data':  data}, default=str)