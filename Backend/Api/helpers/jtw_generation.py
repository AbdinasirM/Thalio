#returns a payload for authentication
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel


#save this into .env
secret = "test"


class jwt_manager:
    @staticmethod
    def encode_jwt(payload_data):
         # Convert Pydantic model to dict and serialize datetimes
        if isinstance(payload_data, BaseModel):
            payload_data = payload_data.dict()
        payload_data['created_at'] = payload_data['created_at'].isoformat()
        payload_data['expires_at'] = payload_data['expires_at'].isoformat()    
        # Create the token
        token = jwt.encode(payload_data, secret, algorithm='HS256')
        print("JWT Token:", token)


    @staticmethod
    def decode_jwt(encoded_token):
        decoded = jwt.decode(encoded_token,  key=secret, algorithms=['HS256'])
        print("Decoded Payload:", decoded)



