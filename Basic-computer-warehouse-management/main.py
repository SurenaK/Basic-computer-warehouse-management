from database import init_db
from gui import open_login_window

if __name__ == "__main__":
    # run database
    init_db()
    # باز کردن پنجره ورود
    open_login_window()