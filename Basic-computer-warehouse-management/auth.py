import hashlib
from database import get_connection

def hash_password(password):
    """هش کردن رمز عبور با SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """بررسی صحت نام کاربری و رمز عبور"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password_hash=?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user is not None



