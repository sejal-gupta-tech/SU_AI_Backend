from pymongo import MongoClient
from app.core.security import get_password_hash

client = MongoClient('mongodb+srv://rinkuyadav9460_db_user:PJrNGHmujot6YovI@cluster0.wrmtwnk.mongodb.net/')
db = client['sevenunique_ai_db']
db['otps'].update_one(
    {'email': 'kratikasharma2003@gmail.com'},
    {'$set': {'otp_hash': get_password_hash('123456')}}
)
print("Updated OTP to 123456")
