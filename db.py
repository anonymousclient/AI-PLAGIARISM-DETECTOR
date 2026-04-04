import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

# MongoDB Atlas connection (from environment variables)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://dv9425959992_db_user:HTy8VMrPnZOhC2jh@cluster0.jvtk0ev.mongodb.net/?appName=Cluster0")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Database
db = client["plagiarism_system"]

# Collections
users_collection = db["users"]
assignments_collection = db["assignments"]
submissions_collection = db["submissions"]
classes_collection = db["classes"]
student_classes_collection = db["student_classes"]
