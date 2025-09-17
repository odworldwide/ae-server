from flask import Flask, request
from flask_cors import CORS
import logging
import sqlite3
import json
import os
import re

dirname = os.path.dirname(__file__)
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

cors = CORS(app)
hurricane = []
market = {}

def new_hurricane():
	global hurricane
	hurricane=[]

def new_point(p):
	global hurricane
	hurricane.append(p)

def update_market(market_state):
	global market
	market = market_state

@app.route("/userchat", methods=["POST"])
def post_chat():
	# u can't say that
	block = False
	blacklist = ["testblacklist", "nigger","nigga", "nigg", "fag", "faggot", "bitch", "whore", "retard", "cunt", "paki", "kike", "coon", "gook"]
	user = request.form['user']
	chat_string = request.form['chat_string']
	for word in blacklist:
		if word in chat_string or word in user:
			block = True
			print('blocked')
	conn = None
	chat = []
	if block == False :
		print('adding to chat')
		try:
			conn = sqlite3.connect(os.path.join(dirname, 'fud.db'))
			c = conn.cursor()
			with conn:
				c.execute("INSERT INTO chat (user,chatString, entityType) VALUES (?,?,?)", (user, chat_string, 'person'))
		except sqlite3.Error as e:
			print(e)
		finally:
			if conn:
				conn.close()
		return 'chat'
	else:
		return "you can't say that"


@app.route("/email", methods=["POST"])
def email():
	email = request.form['email']
	email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
	if(re.search(email_pattern,email)):
		conn = None
		try:
			conn = sqlite3.connect(os.path.join(dirname, 'mail.db'))
			c = conn.cursor()
			with conn:
				c.execute("INSERT INTO mail (email) VALUES (?)", (email,))
		except sqlite3.Error as e:
			print(e)
		finally:
			if conn:
				conn.close()
		return 'valid email'

	else:
		return 'invalid email'


@app.route("/chat", methods=["GET"])
def get_chat():
	conn = None
	chat = []
	try:
		conn = sqlite3.connect(os.path.join(dirname, 'fud.db'))
		c = conn.cursor()
		with conn:
			chatBuf = c.execute('''SELECT * FROM (SELECT * FROM chat ORDER BY id DESC LIMIT 20)Var1 ORDER BY id ASC''')
			for row in chatBuf:
				chat.append({
					'timestamp': row[1],
					'agent': row[2],
					'chat': row[3],
					'entityType': row[4]
				})
		return json.dumps(chat, indent=4, sort_keys=True)

	except sqlite3.Error as e:
		print(e)
	finally:
		if conn:
			conn.close()
	return 'chat'


@app.route("/hurricane", methods=["GET"])
def get_hurricane():
	global hurricane
	return json.dumps(hurricane, indent=4, sort_keys=True)


@app.route("/market", methods=["GET"])
def get_market():
	global market
	return json.dumps(market, indent=4, sort_keys=True)


@app.route("/", methods=["GET"])
def get_all():
	return "blah"

def run():
	app.run(port=5050, host="0.0.0.0", use_reloader=False)

# at the bottom of server.py, after defining get_chat, get_market, get_hurricane:
app.add_url_rule("/fud/chat",      view_func=get_chat,      methods=["GET"])
app.add_url_rule("/fud/market",    view_func=get_market,    methods=["GET"])
app.add_url_rule("/fud/hurricane", view_func=get_hurricane, methods=["GET"])
app.add_url_rule("/fud/userchat",  view_func=post_chat,     methods=["POST"])
