from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost:27017/fintech-db"
client = MongoClient(CONNECTION_STRING)
database = client["fintech-db"]
