from Database.Models.post_model import Post
from Database.Scripts import create_collection
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


from  Database.Scripts import db_connection

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
    @staticmethod
    def create_post(post_text: str, post_image: str, user_id: str):
        # Connect to the db
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]
        post_collection = db["posts"]
        
        # Convert user_id string to ObjectId
        mongo_user_id = ObjectId(user_id)

        # Create Post object
        post_data_combined_data = Post(
            post_text=post_text,
            post_image=post_image,
            created_at=datetime.now(timezone.utc),
            created_user=user_id  # Store as str in the Post model
        )

        # Save the post to the collection
        post_dict = post_data_combined_data.model_dump(mode="json")
        result = post_collection.insert_one(post_dict)

        # Update the user document to include this post ID
        user_collection.update_one(
            {"_id": mongo_user_id},
            {"$push": {"posts": result.inserted_id}}
        )

        print("Post created successfully.")
        return result.inserted_id

    # edit post
    def edit_post(post_id:str, user_id:str,post_text: str, post_image: str):
        
        #connect to db
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]
        post_collection = db["posts"]
        
        #conver the userid into object_id
        converted_user_id = ObjectId(user_id)
        converted_post_id = ObjectId(post_id)
        
        # Build the update dictionary dynamically
        update_fields = {}
        if post_text is not None:
            update_fields["post_text"] = post_text

        if post_image is not None:
            update_fields["post_image"] = post_image
            
        if not update_fields:
            print("Nothing to update.")
            return False
        
        post_collection.update_one(
            {
                "_id":converted_post_id,
                "created_user": user_id            
            },
            {
                "$set":update_fields
            }
        )


    # get a post
    def get_a_post(user_id:str, post_id:str):
        #connect to db
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]
        post_collection = db["posts"]

        #conver the userid into object_id
        converted_user_id = ObjectId(user_id)
        converted_post_id = ObjectId(post_id)
        
     
        post = post_collection.find_one(
             {"_id": converted_post_id,
             "created_user": user_id
             }
        )
        return post

    # get all posts
    def get_all_posts(user_id:str):

        #connect to db
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]
        post_collection = db["posts"]

        #conver the userid into object_id
        converted_user_id = ObjectId(user_id)
        
        #save all the post ids into a list from the user collections
        user = user_collection.find_one(
        {"_id": converted_user_id},
        {"posts": 1, "_id": 0}
        )

        post_id_list = user.get("posts", []) if user else []
        posts = post_collection.find({"_id": {"$in": post_id_list}})

        #in for loop return all the posts that have the same ids in the post id lists
        return list(posts)
    
    # delete post

    # add comment to post