from db import users_collection

student = users_collection.find_one({"role": "student"})
if student:
    print(f"Email: {student['email']}")
    print(f"Password: {student['password']}")
else:
    print("No student user found.")
