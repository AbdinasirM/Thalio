from Database.Scripts import db_connection
import datetime
from dateutil import parser

def verify(email: str, code: int):
    client = db_connection.connect()
    db = client["Data"]
    code_collection = db["verification"]

    # Find the document with the matching email and code
    verification_doc = code_collection.find_one({"email": email, "code": code})
    if not verification_doc:
        return {"success": False, "error": "Verification code not found."}

    # Get the expiration time safely
    expires_at_str = verification_doc.get("expires_at")
    if not expires_at_str:
        return {"success": False, "error": "No expiration date found for this code."}

    try:
        expires_at = parser.parse(expires_at_str)
    except Exception as e:
        return {"success": False, "error": f"Invalid expiration date format: {str(e)}"}

    # Use UTC to avoid timezone mismatch
    now = datetime.datetime.now(datetime.timezone.utc)

    # Check if code has expired
    if now > expires_at:
        return {"success": False, "error": "Verification code has expired."}

    return {"success": True, "message": "Verification code is valid."}
