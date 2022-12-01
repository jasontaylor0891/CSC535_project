import sys
import json
import datetime

from flask_mysqldb import MySQL
from flask import current_app, session
from utility import *

mysql = MySQL()

class ReminderService:
    
    
    def createlist(listname, listdesc, username):

        config = current_app.config
        
        logging.info('Create list process has started')

        try:
            
            cur = mysql.connection.cursor()

            sql = ("INSERT INTO list (listname, listdesc, username) "
            "VALUES('" +listname+ "', '" +listdesc+ "', '" +username+ "')")

            logging.debug(f'SQL Output {sql}')
            results = cur.execute(sql)
            mysql.connection.commit()

            return json.dumps({'Success': 'True'})

        except Exception as e:
            logging.error(f'{str(e)}')
            
            return json.dumps({'Success': 'False','errorcode': '005'})
    
    def displayReminders():
        username = session['username']
        logging.info(f'Displaying reminders for user {username}')

        cur = mysql.connection.cursor()
        #result = cur.execute('SELECT * FROM reminders WHERE username = %s', [username])
        result = cur.execute(
        'select reminders.*, list.listname from reminders LEFT JOIN list on reminders.username = list.username where reminders.username = %s and reminders.listid = list.listid ORDER BY reminders.reminderstartdate;',[username]
        )
       
        if result == 0:
            cur.close()
            return json.dumps({'Auth': 'False','errorcode': '002'})

        if result>0:
            data = cur.fetchall()
            cur.close()
        
        return json.dumps({'Auth': 'True', 'data':  data}, default=str)
        

    def createreminder(rname, rmessage, rstartdate, priority, rlist, username, flag):
        
        logging.debug(f'Create Reminder {rname}')
        logging.debug(f'Flagged? {flag}')
        
        try:

            cur = mysql.connection.cursor()
            results = cur.execute("SELECT listid FROM list WHERE listname = %s AND username = %s", (rlist, username))
            if results>0:
                data = cur.fetchone()
                listid = str(data['listid'])
                logging.debug(f'Output listid {listid}')

           # sql = ("INSERT INTO reminders (remindername, reminderdesc, priority, reminderstartdate, username, listid) "
           # "VALUES('" + rname + "', '" + rmessage + "', '" + priority + "', '" + rstartdate + "', '" + username + "', " + listid + ")")

            sql = "INSERT INTO reminders (remindername, reminderdesc, priority, reminderstartdate, flaged, username, listid) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            record = (rname, rmessage, priority, rstartdate, flag, username, listid)

            logging.debug(f'SQL: {sql}')
            logging.debug(f'Record: {record}')

            results = cur.execute(sql, record)
            mysql.connection.commit()
            cur.close()
            return json.dumps({'Success': 'True'})

        except Exception as e:
            logging.error(f'{str(e)}')
            
            return json.dumps({'Success': 'False','errorcode': '006'})

    def deleteReminder(reminderId):

        cur = mysql.connection.cursor()
        sql = ('DELETE FROM reminders WHERE reminderid =' + str(reminderId))
        logging.debug(f'SQL: {sql}')
        results = cur.execute(sql)
        mysql.connection.commit()

        return json.dumps({'Success': 'True'})

    def filterTheReminder(filterStartDate1,filterEndDate1):
        username = session['username']
        logging.info(f'Displaying reminders for user {username}')

        cur = mysql.connection.cursor()
        #result = cur.execute('SELECT * FROM reminders WHERE username = %s', [username])
        result = cur.execute(
        'select reminders.*, list.listname from reminders LEFT JOIN list on reminders.username = list.username where reminders.username = %s and reminders.listid = list.listid and (reminders.reminderstartdate>=%s and reminders.reminderstartdate<=%s) ORDER BY reminders.reminderstartdate;',[username,filterStartDate1,filterEndDate1]
        )
       
        if result == 0:
            cur.close()
            data = cur.fetchall()
            logging.info(f'Did not find any reminders!')
            
            return json.dumps({'Success': 'False','data': data, 'errorcode': '1'})

        if result>0:
            data = cur.fetchall()
            logging.info(f'Found some reminders in date range!')
            cur.close()
        return json.dumps({'Success': 'True', 'data':  data}, default=str)

    
    def editreminder( rname, rdesc, rpriority, rlist, rstartdate, rem_flagged, username, rId):

        logging.debug(f'Edit Reminder {rname}')
        logging.debug(f'Reminder details received in Reminder service for edit:')
        logging.debug(f'{rname}, {rdesc}, {rpriority}, {rlist}, {rstartdate}, {rem_flagged}, {username}, {rId}')
        
        try:

            cur = mysql.connection.cursor()
            results = cur.execute("SELECT listid FROM list WHERE listname = %s AND username = %s", (rlist, username))

            if results>0:
                data = cur.fetchone()
                listid = str(data['listid'])
                logging.debug(f'Fetch list output {listid}')

            #sql = ("UPDATE reminders SET remindername='" + rname + "', reminderdesc='" + rdesc +"', priority='" + rpriority + "', "
            #"reminderstartdate='" + rstartdate + "', listid=" + listid + " where username='" + username + "' and reminderid=" + str(rId))

            sql="UPDATE reminders SET remindername=%s, reminderdesc=%s, priority=%s, reminderstartdate=%s, flaged=%s, listid=%s where username=%s and reminderid=%s"
            record = (rname, rdesc, rpriority, rstartdate, rem_flagged, listid, username, str(rId))

            logging.debug(f'Edit reminder SQL:  {sql}')
            logging.debug(f'Edit reminder record:  {record}')

            results = cur.execute(sql,record)
            mysql.connection.commit()
            cur.close()
            return json.dumps({'Success': 'True'})

        except Exception as e:
            logging.error(f'{str(e)}')
            return json.dumps({'Success': 'False','errorcode': '009'})
        
    def displayReminderToDelete(reminderId):
        username = session['username']
        logging.info(f'Displaying reminders for user {username}')

        cur = mysql.connection.cursor()
        result = cur.execute(
        'select reminders.*, list.listname from reminders LEFT JOIN list on reminders.username = list.username where reminders.username = %s and reminders.listid = list.listid and reminderid = %s;',[username, reminderId]
        )
       
        if result == 0:
            cur.close()
            return json.dumps({'Auth': 'False','errorcode': '002'})

        if result>0:
            data = cur.fetchall()
            cur.close()
        
        return json.dumps({'Auth': 'True', 'data':  data}, default=str)
    