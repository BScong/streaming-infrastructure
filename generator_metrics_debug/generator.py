#!/usr/bin/env python
from random import randint,uniform,random
import pika
import sys
import json
import time

distinct_categories = ['Alimentation','Boissons','Cigarettes','DepotVentes','Confiseris','FranceTelecom','Grattage','Jounaux','Jouets','Jeux','Librairie','Loto',
				  'Papetrie','Piles','Paysafecard','PCS','Plans','Photocopies','TabacaRouler','Tabletterie','TicketsPremium','TimbresFiscaux','TimbresPoste','Telephonie','Transcash','UniversalMobile',
				  'Carterie','Cdiscount','Intercall','Kertel','	P.Q.N.','P.Q.R.','SFR','DeveloppementPhotos','Publications','Pains']

def generateCategories():
	num_categories = randint(1,10)
	categories = {}
	for i in range(num_categories):
		index = randint(0,len(distinct_categories)-1)
		price = float(("%.2f"%uniform(0.1,200.0)))
		if distinct_categories[index] not in categories:
			categories[distinct_categories[index]] = price
		else:
			categories[distinct_categories[index]] += price
	return categories

time.sleep(15)
i = 0

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.exchange_declare(exchange='sum',
                         exchange_type='fanout')

channel.exchange_declare(exchange='categories',
                         exchange_type='fanout')

while True:
	count = randint(1,20)
	channel.basic_publish(exchange='sum',
	                      routing_key='',
	                      body=str(count))
	categories = generateCategories()
	#print(count, json.dumps(categories))
	channel.basic_publish(exchange='categories',
	                      routing_key='',
	                      body=json.dumps(categories))
	i+=1
