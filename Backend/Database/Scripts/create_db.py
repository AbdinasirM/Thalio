# create_db.py
def create_db(client, db_name):
    try:
        thalio_db = client[db_name]
        return thalio_db
    except Exception as e:
        print("An error has occurred creating a db:", e)