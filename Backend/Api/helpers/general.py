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
    


    
