# from datetime import datetime, timedelta, timezone
# import sys
# import os
# import uuid

# # Dynamically add the parent "Backend" directory to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from database.Scripts.create_db import create_db
# from database.Scripts.create_collection import create_collection
# from database.Scripts import db_connection
# from database.Models.user_model import UserModel

# from database.Models.comment_model import Comment

# # from helpers.forget_password import forget_password
# # from helpers.code_verification import verify
# from helpers.user import User
# # from database.Models.user_model import User
# from helpers.general import General
# from helpers.account import Account


# # myuser = {
# #     "name": "John",
# #     "email": "John@gmail.com",
# #     "password": "Secure444!",
# #     "id": uuid.uuid4(),
# #     "last_name": "Doe",
# #     "profile_image": "",
# #     "online_status": True,

# # }

# # #conver the object above into the user model
# # user = User(**myuser)
# # Account.create_user_account(user)

# # from helpers.email_validation import validate_emails
# # from helpers.password_hashing import hash_password, verify_password
# # from database.Scripts import db_connection
# # from database.Scripts.create_collection import create_collection
# # from database.Models.user_model import UserModel


# # from helpers.general import General

# # Users.all()

# # result = Users.search_user_by_name("John")
# # print(result)
# # result = User.update_name("abdilion7@gmail.com", "newname")
# # print(result)

# # username = "newname"
# # result  =  General.search_user_by_name(username)
# # print(result)



# post_text = "hello world"
# post_image = "682a6c3d01d405e1756485ce"
# user_id = "6833e43573b27b9b02c732a5"
# post_id = "6833bf9648488ca96b754316"

# # try:
# #     post_id = User.create_post(post_text, post_image, user_id)
# #     if post_id:
# #         print("successful")
# #     else:
# #         print("error")
# # except Exception as e:
# #     print("Error from the test:", e)  # Optional for debugging

# # post = User.get_a_post("6822b9997cb3da3916be7f4f", "683390ac1a6ac29e731c40da")
# # print(post)

# # all_posts = User.get_all_posts("6822b9997cb3da3916be7f4f")
# # print(all_posts)

# # result = User.edit_post(post_id,user_id)
# # print(result)

# # result = User.delete_post(post_id,user_id)
# # print(result)

# # result = User.create_post(post_text, post_image, user_id)
# # print(result)
# # from bson import ObjectId

# # mycomment = {
# #     "comment_id":uuid.uuid4(),
# #     "comment_text" : "What city is this?",
# #     "created_at" : datetime.now(timezone.utc),
# #     "user_id" : "6833e43573b27b9b02c732a5",  
# #     "post_id" : "6833ea09d3077d762e9a8d64",
# # }

# # comment = Comment(**mycomment)
# # User.add_comment(comment)

# # result = User.delete_comment("6833e43573b27b9b02c732a5","6833ea09d3077d762e9a8d64","2467b456-0f5e-4ef4-b623-ed9b8c2b0fc9" )
# # result = User.like_a_post("6833ea09d3077d762e9a8d64","6833e4254bd47b56257a5576")
# # print(result)

# # result = User.dislike_a_post("6833ea09d3077d762e9a8d64","6833e4254bd47b56257a5576")
# # print(result)


# #testing the jwt:
# from helpers.jtw_generation import jwt_manager
# from database.Models.jwt_payload_model import Payload

# # my_payload = {
# #     "subject":"test",
# #     "username":"abdi",
# #     "user_id" : 1234,
# #     "created_at": datetime.now(),
# #     "expires_at" :datetime.now()  + timedelta(minutes=5)
# # }


# # payload = Payload(**my_payload)

# # jwt_manager.encode_jwt(payload)

# jwt_manager.decode_jwt("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWJqZWN0IjoidGVzdCIsInVzZXJuYW1lIjoiYWJkaSIsInVzZXJfaWQiOjEyMzQsImNyZWF0ZWRfYXQiOiIyMDI1LTA1LTI5VDIyOjE0OjUwLjIwMTA5NiIsImV4cGlyZXNfYXQiOiIyMDI1LTA1LTI5VDIyOjE5OjUwLjIwMTA5NiJ9.8mXDT_RXXW5d8_UnDE7zp1JFsT-aKgaeVuGty9tL43o")

# # result = General.send_friend_request("6833e4254bd47b56257a5576", "6833e43573b27b9b02c732a5")

# # result = User.accept_friend_request("6833c972421e4fd2c5ac45f1", "6833ca0e9f9a9fa33e715dfe")
# # print(result)

# # result = User.reject_friend_request("6833e43573b27b9b02c732a5", "6833e4254bd47b56257a5576")
# # print(result)

# # def test(email: str, new_password: str, code: int):
# #     verify_result = Account.verify(email, code)

# #     if verify_result.get("success"):
# #         return User.update_password(email, new_password)
# #     else:
# #         print("DEBUG:", verify_result)
# #         return {
# #             "success": False,
# #             "error": "Verification failed. " + verify_result.get("error", "Unknown error")
# #         }
# # from bson import ObjectId


# # with open("images/im.png", "rb") as file:
# #     try:
# #         user_id = ObjectId("6822b9997cb3da3916be7f4f")
# #         User.set_profile_image(file, user_id)
# #     except Exception as e:
# #         print("Error:", e)

# # result = Account.login("john1@gmail.com", "Secure123!")
# # print(result)
# # if __name__ == "__main__":
# #     test_creating_post()
# #    result = test("abdilion7@gmail.com","newpassword",855612)
# #    print(result)
#     # result = Account.verify("abdilion7@gmail.com",866781)
#     # print(result)
#     # Account.forget_password("abdilion7@gmail.com")
#     # create_user_account(user)
#     # result = Account.login("abdilion7@gmail.com", "newpassword")
#     # print(result)



# import gridfs
# from gridfs import GridFSBucket
# print(gridfs)           # should point to something like .../site-packages/gridfs/__init__.py
# print(GridFSBucket)     # should show the class path, e.g. <class 'gridfs.grid_file.GridFSBucket'>
