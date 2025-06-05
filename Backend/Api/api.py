from datetime import datetime, timedelta, timezone
import uuid

from pymongo import MongoClient

from gridfs import GridFSBucket
from bson import ObjectId
from io import BytesIO

from fastapi import FastAPI, HTTPException, Request,UploadFile, File, Form
from pymongo.errors import PyMongoError
from jwt import ExpiredSignatureError, InvalidTokenError
from bson import ObjectId


from database.Models.user_search_request_model import UserSearchRequestModel
from database.Models.update_password_model import UpdatePassword
from database.Models.forget_password_request_model  import ForgetPasswordRequestModel
from database.Models.forget_password_model import Forget_Password
from database.Models.user_model import UserModel 
from database.Models.login_model import LoginRequest
from database.Models.jwt_payload_model import Payload
from database.Models.token_request_model import TokenRequest

from database.Scripts import db_connection
from database.Scripts.create_collection import create_collection

from Api.helpers.account import Account
from Api.helpers.jtw_generation import jwt_manager
from fastapi.encoders import jsonable_encoder


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
@app.post("/forgot_password")
def forget_password(forget_model: ForgetPasswordRequestModel):
      try:
        client = db_connection.connect()
        db = client['Data']
        user_collection = db["users"]
        
        email = forget_model.email

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

#update password
@app.post("/update_password")
def update_password(update_data:UpdatePassword):
        try:
            # Connect to the DB
            client = db_connection.connect()
            db = client["Data"]
            user_collection = db["users"]
            code_collection = db["verification"]

            
            new_password = update_data.new_password
            email = update_data.email
            code = update_data.code

             # 1. Call verify() and check its "success" field explicitly
            result = Account.verify(email, code)
            if not result.get("success", False):
                # Either not found or expired or some other error
                return {"success": False, "error": result.get("error", "Invalid code.")}

            # 2. Hash and update password
            new_hashed = Account.hash_password(new_password)
            update_result = user_collection.update_one({"email": email}, {"$set": {"password": new_hashed}})
            if update_result.matched_count == 0:
                return {"success": False, "error": "User not found."}

            # 3. Delete the used verification code
            code_collection.delete_one({"email": email, "code": code})

            # 4. Send a confirmation email
            Account.send_email(
                recipient=email,
                subject="Password Reset Successful",
                body="Your password has been updated successfully."
            )

            return {"success": True, "message": "Password updated successfully."}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if client:
                client.close()

@app.get("/all_users")
def get_all_users():
    client = None
    try:
        # 1) Connect to the database
        client = db_connection.connect()
        db = client["Data"]
        users_collection = db["users"]
        users = list(users_collection.find())

        # 2) If no users found, return an empty list (or a 404, your choice)
        if not users:
            return {"success": False, "error": "users not found."}

        all_users = []
        for user in users:
              # Convert the main _id
            user["_id"] = str(user["_id"])

            # If there’s a profile_image ObjectId, convert that too
            if isinstance(user.get("profile_image"), ObjectId):
                user["profile_image"] = str(user["profile_image"])

            # 5) Build a safe, minimal dict for each user
            all_users.append({
                "user_id":      user["_id"],
                "first_name":   user.get("name", ""),
                "last_name":    user.get("last_name", ""),
                "profile_image": user.get("profile_image", "")
            })

        return {"success": True, "users": all_users}

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        # 6) Only close client if it was actually created
        if client:
            client.close()

@app.post("/get_user")
def get_current_logged_in(payload: TokenRequest):
    client = None
    try:
        token = payload.token
        user_info = jwt_manager.decode_jwt(token)
        user_id = user_info["user_id"]
        email = user_info["email"]

        client = db_connection.connect()
        db = client["Data"]
        user_collection = db["users"]

        user = user_collection.find_one({
            "_id": ObjectId(user_id),
            "email": email
        })
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Remove sensitive field
        user.pop("password", None)

        # Now ask FastAPI to convert ANY ObjectId (even nested) to str:
        safe_user = jsonable_encoder(
            user,
            custom_encoder={ObjectId: str}
        )
        # safe_user now contains only JSON‐serializable types

        return {"success": True, "user": safe_user}

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")




#search a user by name
@app.get("/search_user_by_name")
def search_user_by_name(request: UserSearchRequestModel):
    try:
        username = request.username
        client = db_connection.connect()
        db = client['Data']
        user_collection = db['users']
        users_found = list(user_collection.find({'name': {'$regex': f'^{username}$', '$options': 'i'}}))
        if not users_found:
            return {"success": False, "error": "no users with that name found."}
        for user in users_found:
            
            # Remove sensitive field
            user.pop("password", None)

            # Now ask FastAPI to convert ANY ObjectId (even nested) to str:
            safe_user = jsonable_encoder(
                user,
                custom_encoder={ObjectId: str}
            )
            return {"success": True, "user": safe_user}
          
    except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired.")
    except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token.")
    except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


#send a friend request
    
#accept friend request

#reject freind request

# get all posts: for the public

# get all posts: that friends posted

# create a post

# like a post

# un like a post