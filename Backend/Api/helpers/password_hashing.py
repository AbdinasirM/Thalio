from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


def hash_password(password):
    try:
        password_hash = PasswordHasher()
        password_to_hash = password_hash.hash(password)
        return password_to_hash
    except Exception as e:
        return ("Error:", e)
    

    
def verify_password(password, hash):
    password_hash = PasswordHasher()
    try:
        password_hash.verify(hash, password)
        return True  # Password matches
    except VerifyMismatchError:
        return False  # Password does not match
    except Exception as e:
        # Handle other exceptions if needed
        return f"Error: {e}"