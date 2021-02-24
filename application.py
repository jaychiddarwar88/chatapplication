import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
import requests
from flask_session import Session
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
import json


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
channelnamelist = []
channelmsg = {}

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# engine = create_engine(DATABASE_URL)
# db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	if not session.get('username'):
		return render_template("loginpage.html")
	else :
		username = session.get('username')
		return render_template("dashboard.html", channellist = channelnamelist, username = username)


@app.route("/login", methods=['POST'])
def loginfunc():
	username = request.form.get('loginusername')
	session['username'] = username
	username = session.get('username')
	return render_template("dashboard.html", channellist = channelnamelist, username = username)


@socketio.on("create channel")
def createchannel(data):
	channelname = data['channelname']
	
	if channelname not in channelnamelist:
		channelmsg[channelname] = []
		channelnamelist.append(channelname)
		channellistjson = json.dumps(channelnamelist)
		emit("new channel", 
			{"channelname" : channelname, "channellist" : channellistjson },
			broadcast = True)
	else :
		print("fail")

@socketio.on("getchatbyname")
def getchanneldetails(data):
	channelname = data['channelname']
	channelname = channelname.replace('\n','')
	channelname = channelname.replace('\t','')
	chatsofchannel = channelmsg[channelname]
	chatsofchannel = json.dumps(chatsofchannel)
	username = json.dumps(session.get('username'))
	emit("chatofchannel", 
		{"channelchat" : chatsofchannel }, 
		broadcast=True)

@socketio.on("msg client")
def msgfunc(data):
	msgdata = data['msgdata']
	channelname = data['channelname']
	channelmsg[channelname].append([msgdata, session.get('username'), str(datetime.now())])
	if len(channelmsg[channelname]) == 101 :
		channelmsg[channelname].pop(0)
	print(len(channelmsg[channelname]))
	emit('sendtoall' ,{"channelname" : channelname});

@socketio.on("delmessage")
def deletemsg(data):
	channelname = data['channelname']
	chattodel = data['chattodel']
	chatindex = 0
	for i in range(len(channelmsg[channelname])):
		if chattodel == channelmsg[channelname][i][2]:
			print(channelmsg[channelname][i][2])
			chatindex = i
	print(channelmsg[channelname])
	channelmsg[channelname].pop(chatindex)
	print(channelmsg[channelname])
	chatsofchannel = json.dumps(channelmsg[channelname])
	emit("chatofchannel", 
		{"channelchat" : chatsofchannel }, 
		broadcast=True)