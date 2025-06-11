from database.Models.post_model import Post
from database.Scripts import create_collection
from dotenv import load_dotenv
from pathlib import Path
import os
import smtplib
from email.message import EmailMessage
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from database.Models.comment_model import  CommentModel

import uuid
import secrets
# import gridfs


from  database.Scripts import db_connection

from database.Models.user_model import UserModel
from helpers.account import Account
from database.Models.userprofile_image_model import UserProfileImage
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

    #set profile image
    @staticmethod
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
    @staticmethod
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
    @staticmethod
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
    @staticmethod
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
    @staticmethod
    def delete_post(post_id:str, user_id:str):
        #connect to db
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]
        post_collection = db["posts"]

        #conver the userid into object_id
        converted_post_id = ObjectId(post_id)
        converted_user_id = ObjectId(user_id)


        post_query = {
        "_id": converted_post_id,
        "created_user": user_id
        
        }
        result = post_collection.delete_one(post_query)
        if result.deleted_count ==1:
            user_collection.update_one(
                {"_id":converted_user_id},
                {"$pull": {"posts":converted_post_id}}
            )
            print("Post deleted successfully")
            return True
        else:
            print("No post deleted. It may not exist or does not belong to this user.")
        return False
    
    @staticmethod
    #accept friend request
    def accept_friend_request(user_id:str, sender_id:str):
        #connect to db
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]

        #conver the userid into object_id
        current_user_id = ObjectId(user_id)
        sender_user_id = ObjectId(sender_id)

        # Step 1: Check if a friend request exists
        user = user_collection.find_one(
            {""
            "_id":current_user_id, 
            "friend_requests_received": sender_id
            },)
        if not user:
            print("No friend request found.")
            return False
        
         # Step 2: Update current user (receiver)
        user_collection.update_one(
            {"_id": current_user_id},
            {
                "$pull": {"friend_requests_received": str(sender_user_id)},
                "$addToSet": {"friends": str(sender_user_id)}
            }
        )

        # Step 3: Update the user who sent the request
        user_collection.update_one(
            {"_id": sender_user_id},
            {
                "$pull": {"friend_requests_sent": str(current_user_id)},
                "$addToSet": {"friends": str(current_user_id)}
            }
        )
        print("Friend request accepted successfully.")
        return True

    @staticmethod
    #reject friend request
    def reject_friend_request(user_id: str, sender_id: str):
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]

        current_user_id = ObjectId(user_id)
        sender_user_id = ObjectId(sender_id)

        # Step 1: Check if a friend request exists
        user = user_collection.find_one(
            {
                "_id": current_user_id,
                "friend_requests_received": str(sender_user_id)
            }
        )

        if not user:
            print("No friend request found.")
            return False

        # Step 2: Remove the friend request
        user_collection.update_one(
            {"_id": current_user_id},
            {"$pull": {"friend_requests_received": str(sender_user_id)}}
        )

        user_collection.update_one(
            {"_id": sender_user_id},
            {"$pull": {"friend_requests_sent": str(current_user_id)}}
        )

        print("Friend request rejected successfully.")
        return True

    @staticmethod
    # add comment to post
    def add_comment(comment:CommentModel):
        #connect to the db
        client = db_connection.connect()
        db = client['Data']
        post_collection = db['posts']

        post_id = ObjectId(comment.post_id)

        # Check if the post exists
        post = post_collection.find_one({"_id": post_id})
        if not post:
            print("Post not found")
            return "Post not found"
        
        # Add the comment to the post
        post_collection.update_one(
            {"_id": post_id},
            {"$push": {"comments": comment.model_dump(mode="json")}}
        )
        print("Comment added successfully.")
        return "Comment added successfully"

    @staticmethod
    # delete comment 
    def delete_comment(user_id:str,post_id:str, comment_id:str):
        #connect to the db
        client = db_connection.connect()
        db = client['Data']
        post_collection = db['posts']

        post_id = ObjectId(post_id)
        user_id = ObjectId(user_id)
        comment_uuid = uuid.UUID(comment_id)  # keep comment_id as UUID

        # Check if the post exists
        post = post_collection.find_one({"_id": post_id})
        if not post:
            print("Post not found")
            return "Post not found"
        
        # delete the comment to the post
        post_collection.update_one(
            {"_id": post_id},
            {"$pull": {"comments":{"comment_id":comment_id}}}
        )
        print("Comment deleted successfully.")
        return "Comment deleted successfully"


    @staticmethod
    def like_a_post(post_id:str, user_id:str):
        #connect to the db
        client = db_connection.connect()
        db = client["Data"]
        
        user_collection = db["users"]
        post_collection = db["posts"]

        current_post_id = ObjectId(post_id)

        current_user_id = ObjectId(user_id)

        
        #check if the user exists
        user = user_collection.find_one(
            {"_id":current_user_id}
        )
        if not user:
            return "user doesn't exist"
        
        #check if the post exists
        post = post_collection.find_one(
            {"_id":current_post_id}
        )
        if not post:
            return "post doesn't exist"

        #add the user id in the likes lists inside the post
        result = post_collection.update_one(
            {"_id":current_post_id},

            {"$addToSet":{"likes":current_user_id}}
        )

        if result.modified_count == 1:
            print("successfully added like to the post")
            return True
        
        else:
           print("Like not added (user may have already liked)")
           return False
        

    @staticmethod
    def dislike_a_post(post_id:str, user_id:str):
        #connect to the db
        client = db_connection.connect()
        db = client["Data"]
        
        user_collection = db["users"]
        post_collection = db["posts"]

        current_post_id = ObjectId(post_id)
        current_user_id = ObjectId(user_id)

        
        #check if the user exists
        user = user_collection.find_one(
            {"_id":current_user_id}
        )
        if not user:
            return "user doesn't exist"
        
        #check if the post exists
        post = post_collection.find_one(
            {"_id":current_post_id}
        )
        if not post:
            return "post doesn't exist"

        dislike_a_post = post_collection.update_one(
            {"_id":current_post_id,
             "likes":current_user_id
             },
             {"$pull":{"likes":current_user_id}}
        )
        if dislike_a_post:
            print("Disliked the post")
            return True
        else:
            print("User didn't like this post")
            return False
        #add the user id in the likes lists inside the post
        

        if dislike_a_post.modified_count == 1:
            print("successfully disliked the post")
            return True
        
        else:
           print("user never liked the post")
           return False


