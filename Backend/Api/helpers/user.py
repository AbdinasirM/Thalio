from dotenv import load_dotenv
from pathlib import Path
import os
import smtplib
from email.message import EmailMessage
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone

import uuid
import secrets
import gridfs


from Database.Scripts import db_connection
from Database.Models.user_model import User
from helpers.account import Account
from Database.Models.userprofile_image_model import UserProfileImage
from bson import ObjectId

class User:

    @staticmethod
        #update password
    def update_password(email: str, new_password: str):
        try:
            # Connect to the DB
            client = db_connection.connect()
            db = client["Data"]
            user_collection = db["users"]

            # Hash the new password
            new_hashed_password = Account.hash_password(new_password)

            # Update the password for the user
            result = user_collection.update_one(
                {"email": email},
                {"$set": {"password": new_hashed_password}}
            )

            # Check if the user was found and updated
            if result.matched_count == 0:
                return {"success": False, "error": "Email not found."}

            # Notify user
            Account.send_email(email, "Password reset successful", "Your password has been updated successfully.")

            return {"success": True, "message": "Password updated successfully."}

        except Exception as e:
            return {"success": False, "error": str(e)}

    #update user profile: name, email, image

    #set profile image
    def set_profile_image(file, user_id):

        # Connect to the correct databases
        client = db_connection.connect()
        file_db = client["FileDB"]
        data_db = client["Data"] 

        user_collection = data_db["users"]
        userprofile_bucket = gridfs.GridFSBucket(file_db)

        # Upload image to GridFS
        file_id = userprofile_bucket.upload_from_stream(
            "profile_image.png",
            file,
            metadata={
                "contentType": "image/png",
                "user_id": user_id  # user_id should be ObjectId
            }
        )

        # Update user document with new image ID
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_image": file_id}}
        )

        if result.modified_count == 0:
            print("User not found or image not updated.")
        else:
            print("File uploaded and user profile image updated.")
            print("File ID:", file_id)

    #update name
    @staticmethod
    def update_name(email:str, new_name:str):
        #connect to the db
        client = db_connection.connect()
        db =client['Data']
        user_collection = db['users']

        user = user_collection.find_one({'email':email})
        if not user:
            return {"success": False, "error": "users not dound."}
        #update the name
        result = user_collection.update_one(
            {"email":email},
            {'$set' : {"name":new_name}}
        )

        
        if result.modified_count == 1:
            return {"success": True, "message": "Name updated successfully."}
        else:
            return {"success": False, "error": "Name update failed or no change made."}

     #send a friend request
        
    #accept friend request

    #reject friend request

    #create post

    #edit post

    #delete post

    # add comment to post

    # like a post

   