from pymongo import MongoClient
from .db_config import host, port, username, password, auth_database

def connect():
    try:
        client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource=auth_database
        )
        # Optional: test connection
        client.admin.command("ping")
        return client
    except Exception as e:
        print("MongoDB connection failed:", str(e))
        raise  # re-raise the exception for the caller to handle
