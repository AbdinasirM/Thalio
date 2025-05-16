from datetime import datetime, timedelta, timezone
import uuid
from Database.Models.forget_password_model import Forget_Password
from helpers.generate_six_digit import generate_code
from helpers.send_email import send_email
from .save_verifaction import save_verification_data
from Database.Scripts import db_connection

def forget_password(email: str):
    try:
        client = db_connection.connect()
        db = client['Data']
        user_collection = db["users"]

        user = user_collection.find_one({"email": email})
        if not user:
            return {"success": False, "error": "Email not found."}

        # Generate 6-digit code
        six_digit_code = generate_code()

        # Create verification record
        verification_data = Forget_Password(
            id=uuid.uuid4(),
            email=email,
            code=six_digit_code,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=6),
            attempt_count=1
        )
        save_verification_data(verification_data)

        # Send email
        subject = "Reset Your Password"
        message_body = f"Your verification code is: {six_digit_code}"
        send_email(email, subject, message_body)

        return {"success": True, "message": "Verification code sent."}

    except Exception as e:
        return {"success": False, "error": str(e)}
