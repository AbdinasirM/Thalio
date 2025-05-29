#returns a payload for authentication
import jwt

#save this into .env
secret = "test"

payload_data = {
    "sub": "4242",
    "name": "Jessica Temporal",
    "nickname": "Jess"
}
def encode_jwt(payload_data):    
    # Create the token
    token = jwt.encode(payload_data, my_secret, algorithm='HS256')
    print("JWT Token:", token)


def decode_jwt(encoded_token):
    decoded = jwt.decode(encoded_token,  key='my_super_secret', algorithms=['HS256'])
    print("Decoded Payload:", decoded)