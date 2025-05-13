from helpers import email_validation, password_hashing
from helpers.email_validation import validate_emails
from helpers.password_hashing import hash_password, verify_password


def sign_in(email, password):
    try:
        '''
        1. fetch all users from the users collection
        2. check if:    
                a. email matches with the user provided email and password hash match
        '''

        hashed_password = hash_password(password)

        
        #return f"email: {normalized_email}, plain text password: {password}, hashed_password: {hashed_password}"
    except Exception as e:
        return f"Error: {e}"