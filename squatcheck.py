import os
import sqlite3
import json
import datetime
import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
   render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
   rv = sqlite3.connect("/var/www/html/squatcheck/squatcheck.db")
   rv.row_factory = sqlite3.Row
   return rv

def get_db():
   if not hasattr(g, 'sqlite_db'):
      g.sqlite_db = connect_db()
   return g.sqlite_db

def init_db():
   db = get_db()
   with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
   db.commit()

@app.cli.command('initdb')
def initdb_command():
   init_db()
   print 'Initialized the database.'

@app.route('/')
def home_page():
   hourData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
   dayData = [0, 0, 0, 0, 0, 0, 0]
   db = get_db()
   cur = db.execute('SELECT COUNT(*) AS entries, hour FROM vibrationEvent WHERE hour > 5 GROUP BY hour ORDER BY hour')
   rows = cur.fetchall()

   for row in rows:
      hourData[row[1] - 7] = row[0]

   cur = db.execute('SELECT COUNT(*) AS entries, dayOfWeek FROM vibrationEvent GROUP BY dayOfWeek ORDER BY dayOfWeek')
   rows = cur.fetchall()

   for row in rows:
      dayData[row[1] - 1] = row[0]

   cur = db.execute('SELECT timestamp FROM vibrationEvent WHERE source = 1 ORDER BY timestamp DESC LIMIT 1')
   leftTimestamp = cur.fetchone()[0]
   cur = db.execute('SELECT timestamp FROM vibrationEvent WHERE source = 2 ORDER BY timestamp DESC LIMIT 1')
   rightTimestamp = cur.fetchone()[0]

   rightTime = time.strftime("%H:%M:%S", time.localtime(rightTimestamp))

   leftTime = time.strftime("%H:%M:%S", time.localtime(leftTimestamp))

   curTime = time.time();

   rightInUse = 1 if curTime - rightTimestamp > 120 else 0
   leftInUse = 1 if curTime - leftTimestamp > 120 else 0


   return render_template('index.html', hourData=hourData, dayData=dayData, leftTime=leftTime, rightTime=rightTime, rightInUse=rightInUse, leftInUse=leftInUse)

@app.route('/addVibrationData', methods=['POST'])
def add_vibration_data():
   db = get_db()
   try:
      data = json.loads(request.data)
   except ValueError, e:
      abort(400)

   source = int(data['vibrationEvent']['source'])
   timeStamp = int(data['vibrationEvent']['timeStamp'])
   dayOfWeek = datetime.datetime.fromtimestamp(timeStamp).weekday()
   hour = datetime.datetime.fromtimestamp(timeStamp).hour

   db.execute('insert into vibrationEvent (source, timeStamp, dayOfWeek, hour) values (?, ?, ?, ?)',
      [source, timeStamp, dayOfWeek, hour])

   db.commit()
   return ('', 201)

@app.teardown_appcontext
def close_db(error):
   if hasattr(g, 'sqlite_db'):
      g.sqlite_db.close()


