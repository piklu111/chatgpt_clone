# auth.py
import sqlite3
from auth_utils import verify_password
from dotenv import load_dotenv
import os

load_dotenv()

# def authenticate(username: str, password: str):
#     conn = sqlite3.connect("users.db")
#     cur = conn.cursor()

#     cur.execute(
#         "SELECT id, password_hash FROM users WHERE username = ?",
#         (username,)
#     )
#     row = cur.fetchone()
#     conn.close()

#     if not row:
#         return None

#     user_id, password_hash = row
#     if verify_password(password, password_hash):
#         return user_id

#     return None
def authenticate(username: str, password: str):
    if (os.getenv("USERS") == username) and (os.getenv("PASSWORD") == password):
        return username
    else :
        return None