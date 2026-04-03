import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# MongoDB Atlas connection (loaded from .env)
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found. Please create a .env file with your MongoDB connection string.")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Database
db = client["plagiarism_system"]

# Collections
users_collection = db["users"]
assignments_collection = db["assignments"]
submissions_collection = db["submissions"]
