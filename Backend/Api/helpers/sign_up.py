from helpers import email_validation, password_hashing
from helpers.password_hashing import hash_password, verify_password
from helpers.email_validation import validate_emails
from Database.Scripts import db_connection
from Database.Scripts.create_collection import create_collection
from Database.Models.user_model import User


def create_user_account(user: User):
    try:
        # Step 1: Validate email
        validated_email = validate_emails(user.email)
        if validated_email.lower().startswith("error"):
            raise ValueError(f"Invalid email: {validated_email}")
        user.email = validated_email

        # Step 2: Hash password
        user.password = hash_password(user.password)

        # Step 3: Connect to DB
        client = db_connection.connect()
        db = client["Data"]
        collection = create_collection(db, "users")

        # Step 4: Validate required fields
        if not all([user.email, user.password, user.name]):
            raise ValueError("User fields cannot be empty")

        # Step 5: Check for duplicates
        if collection.find_one({"email": user.email}):
            raise ValueError("A user with this email already exists.")

        # Step 6: Insert
        collection.insert_one(user.model_dump(mode="json"))

        print("User account created successfully.")

    except Exception as e:
        print("Error occurred:", e)