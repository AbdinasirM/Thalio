import sys
import os

from Database.Scripts.create_db import create_db
from Database.Scripts.create_collection import create_collection
from Database.Scripts import db_connection

# Dynamically add the parent "Backend" directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test():
    try:
        client = db_connection.connect()

        db = create_db(client, "Testing1")

        collection = create_collection(db, "testingcollection")

        collection.insert_one({"hello": "world"})

        print("Document inserted successfully.")

    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    test()
