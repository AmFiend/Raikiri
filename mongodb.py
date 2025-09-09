import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://Glitch:PETnvMU8X0414oW2@glitch.u5ylwcm.mongodb.net/?retryWrites=true&w=majority&appName=Glitch"
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
