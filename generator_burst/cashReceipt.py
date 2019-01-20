from random import randint,uniform,random
import json
import math
import datetime
from time import time, sleep
from collections import OrderedDict
import requests
#import msgpack

def generateLine(ind):
	productCode = '000000'  + str(randint(10,20))
	categoryCode = ""
	productCategoryName = "categoryNamus"
	possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	possibleName=['Boisson','Menu','Sandwich Froid','Viennoiserie','Pain','Sandwich Chaud','Pizza','Patisserie','Confiserie']
	#possibleName=['Alimentation','Boissons','Cigarettes','DepotVentes','Confiseris','FranceTelecom','Grattage','Jounaux','Jouets','Jeux','Librairie','Loto',
	#				  'Papetrie','Piles','Paysafecard','PCS','Plans','Photocopies','TabacaRouler','Tabletterie','TicketsPremium','TimbresFiscaux','TimbresPoste','Telephonie','Transcash','UniversalMobile',
	#				  'Carterie','Cdiscount','Intercall','Kertel','P.Q.N.','P.Q.R.','SFR','DeveloppementPhotos','Publications','Pains']
	productDescription='---'

	index = int(random() * len(possibleName))
	categoryCode += possible[index]
	productCategoryName=possibleName[index]
	taxPercentage=randint(6,20)
	quantity = randint(1,3)
	unitPrice = float(("%.2f"%uniform(0.23,1.10)))
	creditAmount = float(("%.2f"%(unitPrice * quantity)))
	settlementAmount = float(("%.2f"%(creditAmount*(1.+(taxPercentage/100.)))))
	line={
		'lineNumber':ind,
		'productCode':productCode,
		'productDescription':productDescription,
		'productCategoryCode':categoryCode,
		'productCategoryName':productCategoryName,
		'quantity':quantity,
		'unitOfMeasure':'measure',
		'unitPrice':unitPrice,
		'creditAmount':creditAmount,
		'taxPercentage':taxPercentage,
		'settlementAmount':settlementAmount,
	}



	return line

def fromTimeStampToDate(timestamp):
	return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

def truncateFloat(r):
        return float(("%.2f"%(r)));
def generateCashReceipt(cashReceiptid="1",storeid="1",terminalid="1",agentid="1",customerid="1",nblines=randint(1,5),timestamp=time()):
	cashreceipt={
                'cashReceiptID': cashReceiptid,
		'storeID':storeid,
		'terminalID':terminalid,
		'agentID':agentid,
		'customerID':customerid,
		'date':fromTimeStampToDate(timestamp),
		'lines':[generateLine(i+1) for i in range(nblines)]
	}
	netTotal=0.
	grossTotal=0.
	taxPayable=0.
	for i in range(len(cashreceipt['lines'])):
		line = cashreceipt['lines'][i]
		netTotal += line['creditAmount']
		grossTotal += line['settlementAmount']
		taxPayable += line['settlementAmount']-line['creditAmount']


	documentTotal={
		'taxPayable':truncateFloat(taxPayable),
		'netTotal':truncateFloat(netTotal),
		'grossTotal':truncateFloat(grossTotal),
	}

	settlements=[]

	nb_settlements=randint(1,2)
	paymentsMechanismes=["CB","Especes"]
	if nb_settlements==1:
		settlements.append({
			'settlementAmount':grossTotal,
			'paymentMechanism':paymentsMechanismes[randint(0,1)]
		})
	else:
		settlements.append({
			'settlementAmount':truncateFloat(grossTotal- float(("%.2f"%uniform(0.,grossTotal)))),
			'paymentMechanism':paymentsMechanismes[0]
		}),
		settlements.append({
			'settlementAmount':truncateFloat(grossTotal-settlements[0]['settlementAmount']),
			'paymentMechanism':paymentsMechanismes[1]
		})


	cashreceipt['documentTotal']=documentTotal
	cashreceipt['settlements']=settlements
	CRECEIPT=OrderedDict([
                ('cashReceiptID',cashreceipt['cashReceiptID']),
		('storeID',cashreceipt['storeID']),
		('terminalID',cashreceipt['terminalID']),
		('agentID',cashreceipt['agentID']),
		('customerID',cashreceipt['customerID']),
		('date',cashreceipt['date']),
		('lines',cashreceipt['lines']),
		('documentTotal',cashreceipt['documentTotal']),
		('settlements',cashreceipt['settlements'])
	])
	return CRECEIPT

def writeJSON(jsonObject,destination) : ##+'\\'+'overallStatistiques.json'
    with open(destination, 'w', encoding="utf8") as outfile:
        json.dump(jsonObject, outfile, indent=4)


sleep(20)
i = 0
BURST_NUMBER = 10000;
while i<BURST_NUMBER:
	cashRec=generateCashReceipt(i,randint(0,20),randint(0,20),randint(0,20),randint(0,20))
	"""with open('data.msgpack', 'w') as outfile:
		msgpack.pack(data, outfile)
		with open('data.msgpack') as data_file:
		data_loaded = json.load(data_file)
		data_loaded = msgpack.unpack(data_file)"""
	i+=1
	cashRec = json.loads(json.dumps(cashRec))
	# print(cashRec)
	r = requests.post('http://localhost:3000/receipt', json = cashRec)
