from dotenv import load_dotenv
from pathlib import Path
import os
import smtplib
from email.message import EmailMessage
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
from dateutil import parser
import uuid
import secrets

from Database.Scripts import db_connection
from Database.Scripts.create_collection import create_collection
from Database.Models.user_model import User
from Database.Models.forget_password_model import Forget_Password

# Load environment variables
env_path = Path(__file__).resolve().parent / "forget_email_creds" / ".env"
load_dotenv(dotenv_path=env_path)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_PORT = int(os.getenv("PORT", 465))  # Default SSL port
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")


class Account:
    @staticmethod
    def create_user_account(user: User):
        try:
            # Step 1: Validate email
            validated_email = Account.validate_emails(user.email)
            if validated_email.lower().startswith("error"):
                raise ValueError(f"Invalid email: {validated_email}")
            user.email = validated_email

            # Step 2: Hash password
            user.password = Account.hash_password(user.password)

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

    @staticmethod
    def login(email: str, password: str):
        try:
            client = db_connection.connect()
            db = client['Data']
            user_collection = db["users"]

            user = user_collection.find_one({"email": email})
            if not user:
                return {"success": False, "error": "Email not found."}

            if not Account.verify_password(password, user["password"]):
                return {"success": False, "error": "Incorrect password."}

            
            return {
                # "success": True,
                # "user_id": str(user["_id"]),
                # "name": user["name"],
                # "status": user.get("online_status", "offline")
                str(user)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def send_email(recipient, subject, body):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient
        msg.set_content(body)

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
                print("Email sent successfully.")
        except Exception as e:
            print(f"Error sending email: {e}")

    @staticmethod
    def save_verification_data(data: Forget_Password):
        try:
            client = db_connection.connect()
            db = client["Data"]
            verification_collection = db["verification"]
            verification_collection.insert_one(data.model_dump(mode="json"))
            print("Verification data saved.")
        except Exception as e:
            print("Failed to save verification data:", e)

    @staticmethod
    def hash_password(password: str) -> str:
        try:
            password_hash = PasswordHasher()
            return password_hash.hash(password)
        except Exception as e:
            raise Exception(f"Hashing error: {e}")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        password_hash = PasswordHasher()
        try:
            password_hash.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    @staticmethod
    def generate_code() -> str:
        return ''.join(str(secrets.randbelow(10)) for _ in range(6))

    @staticmethod
    def forget_password(email: str):
        try:
            client = db_connection.connect()
            db = client['Data']
            user_collection = db["users"]

            user = user_collection.find_one({"email": email})
            if not user:
                return {"success": False, "error": "Email not found."}

            code = Account.generate_code()

            verification_data = Forget_Password(
                id=uuid.uuid4(),
                email=email,
                code=code,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=6),
                attempt_count=1
            )
            Account.save_verification_data(verification_data)

            Account.send_email(
                recipient=email,
                subject="Reset Your Password",
                body=f"Your verification code is: {code}"
            )

            return {"success": True, "message": "Verification code sent."}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def validate_emails(email_address: str) -> str:
        try:
            email_info = validate_email(email_address, check_deliverability=True)
            return email_info.normalized
        except EmailNotValidError as e:
            return f"Error: {str(e)}"

    @staticmethod
    def verify(email: str, code: int):
        try:
            client = db_connection.connect()
            db = client["Data"]
            code_collection = db["verification"]

            verification_doc = code_collection.find_one({"email": email, "code": code})
            if not verification_doc:
                return {"success": False, "error": "Verification code not found."}

            expires_at_str = verification_doc.get("expires_at")
            if not expires_at_str:
                return {"success": False, "error": "No expiration date found for this code."}

            expires_at = parser.parse(str(expires_at_str))
            now = datetime.now(timezone.utc)

            if now > expires_at:
                return {"success": False, "error": "Verification code has expired."}

            return {"success": True, "message": "Verification code is valid."}

        except Exception as e:
            return {"success": False, "error": str(e)}
