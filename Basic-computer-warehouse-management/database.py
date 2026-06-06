import sqlite3
import hashlib
import os

# مسیر دسکتاپ کاربر (در ویندوز)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
DB_NAME = os.path.join(desktop_path, "warehouse.db")

def get_connection():
    """برقراری ارتباط با دیتابیس"""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """ساخت جداول و درج کاربر پیش‌فرض در صورت نیاز"""
    conn = get_connection()
    c = conn.cursor()

    # جدول کاربران
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )''')

    # جدول قطعات
    c.execute('''CREATE TABLE IF NOT EXISTS parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    buy_price REAL NOT NULL,
                    sell_price REAL NOT NULL,
                    quantity INTEGER DEFAULT 0
                )''')

    # جدول لاگ تراکنش‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (part_id) REFERENCES parts(id)
                )''')

    # اگر کاربری وجود ندارد، کاربر mmd را بساز
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        username = "mmd"
        password = "1234"
        p_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, p_hash))

    conn.commit()
    conn.close()