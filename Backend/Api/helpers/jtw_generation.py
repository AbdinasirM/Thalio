#returns a payload for authentication
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from jwt import ExpiredSignatureError, InvalidTokenError


#save this into .env
secret = "tsdasest"


class jwt_manager:
    @staticmethod
    def encode_jwt(payload_data):
         # Convert Pydantic model to dict and serialize datetimes
        if isinstance(payload_data, BaseModel):
            payload_data = payload_data.dict()
        for field in ['iat', 'exp']:
            val = payload_data.get(field)
            if isinstance(val, datetime):
                payload_data[field] = int(val.timestamp())  
            elif isinstance(val, str):
                # If it's a string, try parsing (e.g., from ISO format)
                try:
                    parsed = datetime.fromisoformat(val)
                    payload_data[field] = int(parsed.timestamp())
                except Exception:
                    raise ValueError(f"{field} must be a datetime or timestamp")

        # Create the token
        token = jwt.encode(payload_data, secret, algorithm='HS256')
        # print("JWT Token:", token)
        return token


    @staticmethod
    def decode_jwt(encoded_token):
        try:
            decoded_token = jwt.decode(
                encoded_token,
                key=secret,
                algorithms=["HS256"],
                options={"require": ["exp"]}  # optional: enforce 'exp' must be present

            )
            return {
                "user_id": decoded_token["user_id"],
                "email": decoded_token["email"]
            }
        except ExpiredSignatureError:
            raise Exception("Token has expired.")
        except InvalidTokenError as e:
            raise Exception(f"Invalid token: {str(e)}")

