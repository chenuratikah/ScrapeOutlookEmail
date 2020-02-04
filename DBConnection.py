from pymongo import MongoClient

client = MongoClient('localhost',27017).get_database("DatabaseName")



