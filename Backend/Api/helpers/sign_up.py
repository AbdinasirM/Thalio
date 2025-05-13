from helpers import email_validation, password_hashing
from helpers.email_validation import validate_emails
from helpers.password_hashing import hash_password, verify_password


def sign_up(email, password):
    try:
        if not email or not password:
            raise ValueError("Email and password are required")

        normalized_email = validate_emails(email)
        hashed_password = hash_password(password)

        return {
            "email": normalized_email,
            "password": password,
            # "hashed_password": hashed_password
        }
    except Exception as e:
        return {"error": str(e)}
