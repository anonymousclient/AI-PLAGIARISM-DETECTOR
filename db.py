from pymongo import MongoClient

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://dv9425959992_db_user:HTy8VMrPnZOhC2jh@cluster0.jvtk0ev.mongodb.net/?appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Database
db = client["plagiarism_system"]

# Collections
users_collection = db["users"]
assignments_collection = db["assignments"]
submissions_collection = db["submissions"]
