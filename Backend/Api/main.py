import sys
import os
import uuid

# Dynamically add the parent "Backend" directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Database.Scripts.create_db import create_db
from Database.Scripts.create_collection import create_collection
from Database.Scripts import db_connection
from Database.Models.user_model import User

myuser = {
    "name": "John",
    "email": "john1@gmail.com",
    "password": "Secure123!",
    "id": uuid.uuid4(),
    "last_name": "Doe",
    "profile_image": "",
    "online_status": True,
    "friend_requests": [],
    "friends": [],
    "posts": []
}

#conver the object above into the user model
user = User(**myuser)

from helpers.email_validation import validate_emails
from helpers.password_hashing import hash_password, verify_password
from Database.Scripts import db_connection
from Database.Scripts.create_collection import create_collection
from Database.Models.user_model import User








if __name__ == "__main__":
    # create_user_account(user)
    # result = login("john1@gmail.com", "Secure123!")
    # print(result)





