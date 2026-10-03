from pymongo import MongoClient

uri = "mongodb+srv://heartlesshero1289_db_user:<db_password>@cluster0.if6ug0w.mongodb.net/?appName=Cluster0"

client = MongoClient(uri)

try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()

except Exception as e:
    raise Exception(
        "The following error occurred: ", e)