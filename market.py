import sqlite3
import os
import chat
import math
import random
import server
import helpers
import json
import scipy.stats
import numpy as np

dirname = os.path.dirname(__file__)
agents = []
company_names = ['Eclipse Re Ltd. (Series 2020-04A)']

#market sets price based on value?
#value of a bid vs value of an ask
class Market:
	global agents
	bonds=[]
	bid_list=[]
	ask_list=[]
	initial_funds=0
	current_funds=0

	def __init__(self, initial_price, issuing_company):
		self.price = initial_price
		self.initial_price = initial_price
		self.issuing_company = issuing_company

	def update_price(self, p):
		self.price = round(p, 2)

	def add_company(self, company):
		self.issuing_company = company

market = Market(100, 'Eclipse Re Ltd. (Series 2020-04A)')

#the owner of the bond determines their 'price'
class Bond:
	def __init__(self, initial_price, bond_yield, period, company):
		self.initial_price = initial_price
		self.price = initial_price
		self.bond_yield = bond_yield
		self.bond_period = period
		self.company = company

	def yield_per_unit_time(self):
		return (self.bond_yield*self.initial_price)/self.bond_period

	def est_return(self, time_remaining):
		est = ((self.initial_price - self.price) + (time_remaining*self.bond_yield*self.initial_price)/self.bond_period)/self.price + 1
		return est

	def update_price(self, p):
		self.price = round(p, 2)


#volume is in dollars, est return is the number of
#dollars you get back for what you put in
class Bid:
	def __init__(self, desired_return, price, vol, bidder):
		self.desired_return = desired_return
		self.price = price
		self.vol = vol
		self.bidder = bidder


class Ask:
	def __init__(self, est_return, price, num, asker):
		self.est_return = est_return
		self.price = price
		self.num = num
		self.asker = asker

class Agent:
	bonds=[]

	def __init__(self, name, risk_mean, risk_std, funds):
		self.name = name
		self.risk_mean = risk_mean
		self.risk_std = risk_std
		self.initial_funds = funds
		self.funds = funds

	def buy_limit(self):
		return self.funds/10

	def trade(self, risk, time_remaining):
		#initially, reset each time
		self.bid=None
		self.ask=None
		if len(self.bonds) > 0:
			# print('agent', self.name, 'has', len(self.bonds), 'bonds and $', self.funds)
			if risk > self.risk_mean + 1.5*self.risk_std:
				desperation = self.desperation(risk)
				for bond in self.bonds:
					bond.update_price(bond.initial_price - bond.initial_price*desperation)
				if random.random() > 0.9: 
					chat.selling(self.name)
				sellNum = len(self.bonds)
				if sellNum > 0:
					self.ask = Ask(self.bonds[0].est_return(time_remaining), self.bonds[0].price, sellNum, self.name)
					# print(self.name, 'asks', self.ask.est_return, self.ask.price, self.ask.num)

		elif risk < self.risk_mean + 1.0*self.risk_std and risk > self.risk_mean - 1.0*self.risk_std:
			eagerness = self.eagerness(risk)
			if random.random() > 0.97:
				chat.buying(self.name)
			desired_return=1.05
			self.bid = Bid(desired_return, eagerness*market.initial_price, self.buy_limit(), self.name)

	def desperation(self, risk):
		# desperation is the fraction of money you are willing to lose
		# goes up to 70%
		desp = (0.7/self.risk_std)*(risk - (self.risk_mean + 1.5*self.risk_std))**2
		# print('getting desperation', self.name, risk, self.risk_mean, self.risk_std, desp)
		return desp

	def earnings(self):
		# eagerness is how much you're wanting to buy a bond for, relative to ask price
		earnings = (self.funds - self.initial_funds)/self.funds
		# if earnings != 0.0: print(self.name, 'current earnings are', round(earnings,2), '%')
		return earnings

	def eagerness(self, risk):
		#eagerness increases within 1s.d. of mean
		dist = scipy.stats.norm(self.risk_mean, self.risk_std/3)
		eagerness = 0.9 + dist.pdf(risk)/(dist.pdf(self.risk_mean)*2)

		#scale for sqrt earnings -> more $ = more 
		eagerness = eagerness*math.sqrt(self.earnings() + 1)
		return eagerness


def load_companies():
	global company_names
	with open(os.path.join(dirname,'./companies.txt'), newline='') as f:
		company_names = f.read().split('\n')

def issue_bonds(price, bond_yield, num_bonds, bond_period):
	global market
	for b in range(0, num_bonds):
		bond = Bond(price, bond_yield, bond_period, market.issuing_company)
		market.bonds.append(bond)
	chat.update('market', '##### NEW CAT DROP #####', 'market')
	chat.update('market', market.issuing_company + " has released a tranche of " + str(num_bonds) + " bonds", 'market')
	print(market.issuing_company, "has released a tranche of", num_bonds, "bonds")

def shuffle():
	global agents, market
	random.shuffle(agents)

	#add some noise to the market price
	noise = np.random.normal(0,1)
	market.price = market.price + noise

def rand_agent():
	global agents
	return random.choice(agents)

def get_state():
	global agents, market
	market.current_funds = 0
	for agent in agents:
		market.current_funds = market.current_funds + agent.funds

def create_agents():
	global agents, market
	with open(os.path.join(dirname, 'names.txt'),'r') as f_open:
		names = f_open.read()
		for name in names.split('\n'):
			risk_mean = round(0.8*random.random(), 2)
			risk_std = round(0.1*random.random() + 0.06, 2)
			funds = 5000 + round(random.random()*10000)
			market.initial_funds = market.initial_funds + funds
			agents.append(Agent(name, risk_mean, risk_std, funds))

def agent_trade(risk, time_remaining):
	global agents
	for agent in agents:
		agent.trade(risk, time_remaining)

#this could belong to World?
def calculate_buy_sell_lists():
	global agents, market
	market.ask_list = []
	market.bid_list = []

	for agent in agents:
		if agent.bid:
			market.bid_list.append(agent.bid)

		elif agent.ask:
			market.ask_list.append(agent.ask)

	if len(market.ask_list) > 0:
		sum_asks = 0
		#calculate market price
		for ask in market.ask_list:
			sum_asks = sum_asks + ask.price

		market.update_price(sum_asks/len(market.ask_list))


	if len(market.bid_list) > 0:
		sum_bids = 0
		for bid in market.bid_list:
			sum_bids = sum_bids + bid.price

		market.update_price((market.price + sum_bids/len(market.bid_list))/2)


		# market.update_price(sum_asks/len(market.ask_list) + sum_bids/len(market.ask_list))
	# print('market price for bonds is', market.price)



def yield_payout():
	global agents
	for agent in agents:
		for bond in agent.bonds:
			agent.funds = round(agent.funds + bond.yield_per_unit_time(), 2)


def loss_event():
	global agents
	for agent in agents:
		if len(agent.bonds) > 0:
			#chat.loss_event goes here
			if random.random() > 0.4: chat.loss(agent.name)
			# print('agent', agent.name, 'made a loss of', agent.bonds[0].initial_price*len(agent.bonds))
		agent.bonds = []

def reset_market(time_remaining):
	global market, agents
	market.bonds = []
	market.add_company(random.choice(company_names))
	for agent in agents:
		if len(agent.bonds) > 0:
			for bond in agent.bonds:
				payout = round(bond.initial_price + bond.yield_per_unit_time()*time_remaining, 2)
				agent.funds = agent.funds + payout
			if random.random() > 0.7: chat.win(agent.name)
		agent.bid = None
		agent.ask = None
		agent.bonds = []

def run_exchange(risk, time_remaining):
	global agents, market
	calculate_buy_sell_lists()
	server.update_market(helpers.get_json(market))
	#print("risk is", risk)
	for bid in market.bid_list:
		bid_agent = next((agent for agent in agents if agent.name == bid.bidder), None)

		# if there are market bonds to sell
		if len(market.bonds) > 0:
			price = market.bonds[0].initial_price
			est_return = market.bonds[0].est_return(time_remaining)
			# print('est return is', est_return, 'desired return is', bid.desired_return)

			if est_return > bid.desired_return:
				num_bonds = math.floor(bid.vol/float(price))

				if num_bonds > 0:
					#if not enough, sell all the bonds in the market to the agent
					if num_bonds > len(market.bonds):
						num_bonds = len(market.bonds)

					#concatenate
					bid_agent.bonds = bid_agent.bonds + market.bonds[:num_bonds]
					bid_agent.funds = bid_agent.funds-price*num_bonds

					#update the bid volume
					bid.vol = bid.vol-price*num_bonds

					#remove from the market
					market.bonds = market.bonds[num_bonds:]
					if random.random() > 0.7:
						chat.update('market', bid_agent.name + ' just bought ' + str(num_bonds) + ' bonds, leaving ' + str(len(market.bonds)) + ' remaining in this tranche', 'market')

				if len(market.bonds) == 0:
					chat.update('market', 'all the bonds in the ' + market.issuing_company + ' tranche have now been sold', 'market')

		#then, if there are asks
		if len(market.ask_list) > 0:

			for index, ask in enumerate(market.ask_list):
				ask_agent = next((agent for agent in agents if agent.name == ask.asker), None)
				price = market.price
				if ask.num > 0:
					if ask.est_return > bid.desired_return and price < bid.price:
						num_bonds = math.floor(bid.vol/price)
						if num_bonds > 0:
							if num_bonds > ask.num:
								num_bonds = ask.num

							# print('asker has', len(ask_agent.bonds), 'bidder has ', len(bid_agent.bonds))
							bid_agent.bonds = bid_agent.bonds + ask_agent.bonds[:num_bonds]
							bid_agent.funds = bid_agent.funds-price*num_bonds

							ask_agent.bonds = ask_agent.bonds[num_bonds:]
							ask_agent.funds = ask_agent.funds+price*num_bonds

							#update the ask
							ask.num = ask.num - num_bonds

							#update the bid
							bid.vol = bid.vol-price*num_bonds

							# print(ask_agent.name, 'sold', num_bonds, 'bonds to ', bid_agent.name, 'at', price)
							chat.update('market', ask_agent.name + ' sold ' + str(num_bonds) + ' bonds to ' + str(bid_agent.name), 'market')

