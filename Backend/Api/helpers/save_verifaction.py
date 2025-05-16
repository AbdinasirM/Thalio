from Database.Models.forget_password_model import Forget_Password
from Database.Scripts import db_connection

def save_verification_data(data: Forget_Password):
   try:
       # 1. Connect to the DB
        client = db_connection.connect()

        # 2. Access the database and collection
        db = client["Data"]
        verification_collection = db["verification"]

        # 3. Insert the document (use model_dump to get a JSON-safe dict)
        verification_collection.insert_one(data.model_dump(mode="json"))

        print("Verification data saved.")
   except Exception as e:
         print("Failed to save verification data:", e)
      
