import sys
from pathlib import Path

# ✅ Add the 'Api/' directory (2 levels up) to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

# ✅ Now imports will work
from Database.Scripts import db_connection
import gridfs

# Connect to the DB
client = db_connection.connect()
db = client["FileDB"]
image_collection = db["images"]

userprofile_bucket = gridfs.GridFSBucket(db)

print("done")
