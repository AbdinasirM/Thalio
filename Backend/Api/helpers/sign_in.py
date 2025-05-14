from helpers import email_validation, password_hashing
from helpers.password_hashing import hash_password, verify_password
from helpers.email_validation import validate_emails
from Database.Scripts import db_connection
from Database.Scripts.create_collection import create_collection
from Database.Models.user_model import User

def login(email: str, password: str):
    try:
        # 1. Connect to DB
        client = db_connection.connect()
        db = client['Data']
        user_collection = db["users"]

        # 2. Find user by email
        user = user_collection.find_one({"email": email})
        if not user:
            return {"success": False, "error": "Email not found."}

        # 3. Verify password
        if not verify_password(password, user["password"]):
            return {"success": False, "error": "Incorrect password."}

        # 4. Login successful
        return {"success": True, "user_id": str(user["_id"]), "name": user["name"], "status" : user["online_status"]}

    except Exception as e:
        return {"success": False, "error": str(e)}