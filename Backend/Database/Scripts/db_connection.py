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
        print("Connected to MongoDB.")
        return client
    except Exception as e:
        print("Connection failed:", e)
        raise