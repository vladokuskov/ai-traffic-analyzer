from pymongo import MongoClient
import os

# MongoDB URI connection string from environment variable or default to 'mongodb://mongo:27017/'
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")

# Connect to MongoDB client using the specified URI
client = MongoClient(MONGO_URI)

# Select the 'anomalies' database in MongoDB
db = client.anomalies

# Select the 'detections' collection within the 'anomalies' database
collection = db.detections
