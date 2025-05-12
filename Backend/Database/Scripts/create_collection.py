def create_collection(db, collection_name):
    try:
        
        # Get or create the collection
        collection = db[collection_name]
        print(f"Collection '{collection_name}' accessed or created.")
       
        return collection
    except Exception as e:
        print("An error has occurred while creating/accessing the collection:", e)
