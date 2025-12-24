import pymongo
import os

# Use environment variable for security (better than hardcoding)
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB client (one per bot)
client = pymongo.MongoClient(MONGO_URI)

# MASTER DATABASE
folder = client["MASTER_DATABASE"]
usersdb = folder["USERSDB"]
chats_auth = folder["CHATS_AUTH"]
gcdb = folder["GCDB"]

# SKS DATABASE
sks_folder = client["SKS_DATABASE"]
sksdb = sks_folder["SKS"]
confdb = sks_folder["CONF_DATABASE"]

# Shopify bot database
shopifybot_db = client["shopifybot_db"]
usersites_collection = shopifybot_db["usersites"]

print("MONGODB CONNECTED ✅")
