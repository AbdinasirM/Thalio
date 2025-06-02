from datetime import datetime, timedelta

from pymongo import MongoClient

from gridfs import GridFSBucket
from bson import ObjectId
from io import BytesIO

from fastapi import FastAPI, HTTPException, Request,UploadFile, File, Form
from pymongo.errors import PyMongoError
from jwt import ExpiredSignatureError, InvalidTokenError
from bson import ObjectId


from database.Models.user_model import UserModel 
from database.Models.login_model import LoginRequest
from database.Models.jwt_payload_model import Payload
from database.Models.token_request_model import TokenRequest

from database.Scripts import db_connection
from database.Scripts.create_collection import create_collection

from Api.helpers.account import Account
from Api.helpers.jtw_generation import jwt_manager


app = FastAPI()

@app.post("/sign_up")
def sign_up(user: UserModel):
    try:
        # Validate email
        validated_email = Account.validate_emails(user.email)
        if validated_email.lower().startswith("error"):
            raise ValueError(f"Invalid email: {validated_email}")

        # Hash password
        hashed_password = Account.hash_password(user.password)

        # Connect to DB
        client = db_connection.connect()
        db = client["Data"]
        collection = create_collection(db, "users")

        # Validate required fields
        if not all([user.name, user.email, user.password]):
            raise ValueError("User fields cannot be empty")

        # Check for duplicates
        if collection.find_one({"email": validated_email}):
            raise ValueError("A user with this email already exists.")

        # Insert new user
        user_dict = user.model_dump(mode="json")
        user_dict["email"] = validated_email
        user_dict["password"] = hashed_password
        collection.insert_one(user_dict)

        print("User account created successfully.")
        return {"message": "User account created successfully"}
    except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        try:
            client.close()
        except:
            pass

@app.post("/sign_in")
def sign_in(request: Request, body:LoginRequest):
        try:
            
            # Connect to DB
            client = db_connection.connect()
            db = client['Data']
            user_collection = db["users"]

            email = body.email
            password = body.password

            #check if the user exists
            user = user_collection.find_one({"email": email})
            if not user or not Account.verify_password(password, user["password"]):
                return {"success": False, "error": "Invalid email or password."}
           
            #conver the user id into string from uuid
            user["_id"] = str(user["_id"])

            # Clean sensitive fields before returning
            user.pop("password", None)
            payload = {
                "subject":"sign_in",
                "user_id":str(user["_id"]),
                "email":user["email"],
                "iat": datetime.now(),
                "exp" :datetime.now()  + timedelta(minutes=1)
            }

            m_payload = Payload(**payload)
            token = jwt_manager.encode_jwt(m_payload)

            return {
                "success": True,
                "token": token
            }
        
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
        finally:
            try:
                client.close()
            except:
                pass

@app.get("/all_users")
def get_all_users():
        
        try:
            #connect to the db
            client = db_connection.connect()
            db = client['Data']
            users_collection = db['users']
            users = list(users_collection.find())
            if not users:
                        return {"success": False, "error": "users not dound."}
            
            all_users = []

            for user in users:
                #conver the user id into string from uuid
                user["_id"] = str(user["_id"])

                # Clean sensitive fields before returning
                user.pop("password", None)
                all_users.append( {"user_id":user['_id'], "first_name":user['name'], "last_name":user['last_name'], "Profile Image":user['profile_image']})
            return {"success": True, "users": all_users}
        
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        finally:
            try:
                client.close()
            except:
                pass

@app.post("/get_user")
def get_current_logged_in(payload: TokenRequest):
    try:
        token = payload.token

        # Decode the token
        user_info = jwt_manager.decode_jwt(token)

        user_id = user_info["user_id"]
        email = user_info["email"]

        # Connect to the DB
        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]

        user = user_collection.find_one({
            "_id": ObjectId(user_id),
            "email": email
        })

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        user["_id"] = str(user["_id"])
        user.pop("password", None)

        return {"success": True, "user": user}

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        try:
            client.close()
        except:
            pass

@app.post("/set_profile_img")
def set_profile_image(
    file: UploadFile = File(...),
    token: str = Form(...)
    ):
    try:
        # 1. Decode JWT → get string user_id, convert to ObjectId
        user_decoded = jwt_manager.decode_jwt(token)
        user_obj_id = ObjectId(user_decoded["user_id"])

        # 2. Connect to MongoDB
        client = db_connection.connect()
        file_db = client["FileDB"]
        data_db = client["Data"]
        user_coll = data_db["users"]

        # 3. Create a GridFSBucket on FileDB
        fs_bucket = GridFSBucket(file_db)

        # 4. Read file bytes and wrap in BytesIO
        contents = file.file.read()
        stream = BytesIO(contents)

        # 5. Upload via GridFSBucket.upload_from_stream
        new_file_id = fs_bucket.upload_from_stream(
            file.filename or "profile_image.png",
            stream,
            metadata={
                "contentType": file.content_type,
                "user_id": user_obj_id
            }
        )

        # 6. Update user’s profile_image with new_file_id
        result = user_coll.update_one(
            {"_id": user_obj_id},
            {"$set": {"profile_image": new_file_id}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found.")

        return {"success": True, "message": "File uploaded and profile image updated"}

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        try:
            client.close()
        except:
            pass

#forget password

#update password
#send a friend request
    
#search a user by name

#accept friend request

#reject freind request

#get all posts: for the public

#get all posts: that friends posted

#create a post

#like a post

#un like a post


