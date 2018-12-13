import pprint
import datetime
import time
from pymongo import MongoClient
client = MongoClient('mongo', 27017)
db = client.receipt_database
collection = db.receipt
post = {"author": "Mike","text": "My first blog post!","tags": ["mongodb", "python", "pymongo"], "date": datetime.datetime.utcnow()}
collection.insert_one(post)

pprint.pprint(collection.find_one())
