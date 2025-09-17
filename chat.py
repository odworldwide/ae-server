import sqlite3
import os
import csv
import time
import random
import re
import unidecode

import market

dirname = os.path.dirname(__file__)
db_file = os.path.join(dirname, 'fud.db')

buy_chat = []
sell_chat = []
outer_chat = []
win_chat = []
loss_chat = []
landfall_chat = []
prox_chat = []
generic_chat = []


class OuterChat:
	def __init__(self, unique_id, agent, phrase, tag, branch, entity_type):
		self.unique_id = unique_id
		self.agent = agent
		self.phrase = phrase
		self.tag = tag
		self.branch = branch
		self.entity_type = entity_type

class Chat:
	def __init__(self, agent, phrase, entity_type):
		self.agent = agent
		self.phrase = phrase
		self.entity_type = entity_type

#load in chat csvs as objects
def load_chats():
	with open(os.path.join(dirname,'./chat_data/outer_loop.csv'), newline='') as f:
		reader = csv.reader(f)
		for row in reader:
			outer_chat.append(OuterChat(row[0], row[1], row[2], row[3], row[4], 'agent'))

	with open(os.path.join(dirname,'./chat_data/buying.csv'), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			buy_chat.append(Chat(market.rand_agent().name, row[0], 'agent'))

	with open(os.path.join(dirname,'./chat_data/selling.csv'), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			sell_chat.append(Chat(market.rand_agent().name, row[0], 'agent'))

	with open(os.path.join(dirname,'./chat_data/win.csv'), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			win_chat.append(Chat(market.rand_agent().name, row[0], 'agent'))

	with open(os.path.join(dirname,'./chat_data/loss.csv'), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			loss_chat.append(Chat(market.rand_agent().name, row[0], 'agent'))

	with open(os.path.join(dirname,'./chat_data/prox.csv'), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			prox_chat.append(Chat(market.rand_agent().name, row[0], 'agent'))

	with open(os.path.join(dirname,'./chat_data/landfall.csv'), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			landfall_chat.append(Chat(market.rand_agent().name, row[0], 'agent'))

	with open(os.path.join(dirname,'./chat_data/smalltalk.csv'), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			generic_chat.append(Chat(market.rand_agent().name, row[0], 'agent'))


def buying(agent):
	global buy_chat
	chat = random.choice(buy_chat)
	update(agent, chat.phrase, 'agent')
	# print(agent, chat.phrase)

def selling(agent):
	global sell_chat
	chat = random.choice(sell_chat)
	update(agent, chat.phrase, 'agent')
	# print(agent, chat.phrase)

def win(agent):
	global win_chat
	chat = random.choice(win_chat)
	update(agent, chat.phrase, 'agent')

def loss(agent):
	global loss_chat
	chat = random.choice(loss_chat)
	update(agent, chat.phrase, 'agent')

def prox(city):
	global prox_chat
	chat = random.choice(prox_chat)
	name = city['name']
	if random.random() > 0.4:
		name = unidecode.unidecode(name)
	if random.random() > 0.4:
		name = name.lower()
	phrase = re.sub('#name#', name, chat.phrase)
	phrase = re.sub('#dist#', str(int(round(city['distance']))), phrase)
	phrase = re.sub('#pop#', str(int(round(city['pop'], -3))), phrase)
	print('!!!!!!!!', phrase, chat.agent)
	update(chat.agent, phrase, 'agent')

def landfall():
	global landfall_chat
	chat = random.choice(landfall_chat)
	update(chat.agent, chat.phrase, 'agent')

def outer_loop(line, risk):
	if line[3] == 'End' or line[3] == 'One':
		update(line[1], line[2], 'agent')
		time.sleep(round(random.random()*150) + 200)
	else:
		update(line[1], line[2], 'agent')
		time.sleep(round(random.random()*100)+20)

def chatter():
	global generic_chat
	chat = random.choice(generic_chat)
	print(chat.agent, chat.phrase)
	update(chat.agent, chat.phrase, 'agent')

def init_db():
	global db_file
	conn = None
	try:
		conn = sqlite3.connect(db_file)
		c=conn.cursor()
		c.execute('''DROP TABLE IF EXISTS chat''')
		c.execute('''CREATE TABLE IF NOT EXISTS chat
			(id INTEGER PRIMARY KEY, 'timestamp' DATETIME DEFAULT CURRENT_TIMESTAMP, user TEXT, chatString TEXT, entityType TEXT)''')
		print(sqlite3.version)
	except sqlite3.Error as e:
		print(e)
	finally:
		if conn:
			conn.close()


def update(agent, chat_string, entity_type):
	global db_file
	conn = None
	try:
		conn = sqlite3.connect(db_file)
		c = conn.cursor()
		with conn:
			c.execute("INSERT INTO chat (user,chatString,entityType) VALUES (?,?,?)", (agent, chat_string, entity_type))
	except sqlite3.Error as e:
		print(e)
	finally:
		if conn:
			conn.close()