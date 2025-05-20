import sys
import os
import uuid

# Dynamically add the parent "Backend" directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from Database.Scripts.create_db import create_db
# from Database.Scripts.create_collection import create_collection
from Database.Scripts import db_connection
# from Database.Models.user_model import User
# from helpers.forget_password import forget_password
# from helpers.code_verification import verify

from helpers.account import Account


# myuser = {
#     "name": "John",
#     "email": "john1@gmail.com",
#     "password": "Secure123!",
#     "id": uuid.uuid4(),
#     "last_name": "Doe",
#     "profile_image": "",
#     "online_status": True,
#     "friend_requests": [],
#     "friends": [],
#     "posts": []
# }

# #conver the object above into the user model
# user = User(**myuser)

# from helpers.email_validation import validate_emails
# from helpers.password_hashing import hash_password, verify_password
# from Database.Scripts import db_connection
# from Database.Scripts.create_collection import create_collection
# from Database.Models.user_model import User

from helpers.user import User

from helpers.users import Users

# Users.all()

result = Users.search_user_by_name("John")
print(result)
# def test(email: str, new_password: str, code: int):
#     verify_result = Account.verify(email, code)

#     if verify_result.get("success"):
#         return User.update_password(email, new_password)
#     else:
#         print("DEBUG:", verify_result)
#         return {
#             "success": False,
#             "error": "Verification failed. " + verify_result.get("error", "Unknown error")
#         }
# from bson import ObjectId


# with open("images/im.png", "rb") as file:
#     try:
#         user_id = ObjectId("6822b9997cb3da3916be7f4f")
#         User.set_profile_image(file, user_id)
#     except Exception as e:
#         print("Error:", e)

    







# if __name__ == "__main__":
#    result = test("abdilion7@gmail.com","newpassword",855612)
#    print(result)
    # result = Account.verify("abdilion7@gmail.com",866781)
    # print(result)
    # Account.forget_password("abdilion7@gmail.com")
    # create_user_account(user)
    # result = Account.login("abdilion7@gmail.com", "newpassword")
    # print(result)




