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
from Database.Models.comment_model import Comment
from helpers.account import Account
from Database.Models.userprofile_image_model import UserProfileImage
from bson import ObjectId


class General :

    #return all users for the public people side
    @staticmethod
    def all():
        #connect to the db
        client = db_connection.connect()
        db = client['Data']
        users_collection = db['users']
        users = list(users_collection.find())
        if not users:
                    return {"success": False, "error": "users not dound."}

        for user in users:
            print(f"User ID: {user['_id']}, Name: {user['name']}, Last Name: {user['last_name']}, Profile Image: {user['profile_image']}")

    #search a user
    @staticmethod
    def search_user_by_name(username:str):
          #connect to the db
            client = db_connection.connect()
            db = client['Data']
            user_collection = db['users']
            users_found = list(user_collection.find({'name': {'$regex': f'^{username}$', '$options': 'i'}}))
            if not users_found:
                  return {"success": False, "error": "no users with that name found."}
            for user in users_found:
                 return (f"User ID: {user['_id']}, Name: {user['name']}, Last Name: {user['last_name']}, Profile Image: {user['profile_image']}")
            # return {"success": True, "users": users_found}

    #return all the data for the current logged in user: user stuff, posts, friends

    @staticmethod
    #send a friend request
    def send_friend_request(current_user_id:str,friend_id:str):
        #connect to the db
        client = db_connection.connect()
        db =client['Data']
        user_collection = db['users']
        converted_current_user_id = ObjectId(current_user_id)
        converted_friend_id = ObjectId(friend_id)
        

        # Update the recipient's 'friend_requests_received'
        friend_result = user_collection.update_one(
            {"_id": converted_friend_id},
            {"$addToSet": {"friend_requests_received": str(converted_current_user_id)}}
        )

        # Update the sender's 'friend_requests_sent'
        current_user_result = user_collection.update_one(
            {"_id": converted_current_user_id},
            {"$addToSet": {"friend_requests_sent": str(converted_friend_id)}}
        )

        if friend_result.modified_count == 1 and current_user_result.modified_count == 1:
            print("Friend request sent successfully.")
            return True
        else:
            print("Failed to send friend request.")
            return False
        


        #return boolean

    

    # like

    #remove like




    
