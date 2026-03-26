import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://spydechk:Ofqfcb3m@cluster0.ucczpx3.mongodb.net/?appName=Cluster0"
)

try:
    print("MONGODB CONNECTED SUCCESSFULLY ✅")
except:
    print("MONGODB CONNECTION FAILED ❌")

folder = client["MASTER_DATABASE"]
usersdb = folder["USERSDB"]
chats_auth = folder["CHATS_AUTH"]
gcdb = folder["GCDB"]

sks_folder = client["SKS_DATABASE"]
sksdb = sks_folder["SKS"]
confdb = sks_folder["CONF_DATABASE"]
