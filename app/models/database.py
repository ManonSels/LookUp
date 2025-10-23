import sqlite3
import os
from flask import g
import hashlib

# ----- DB CONNECTION ----- #
class DBConnection:
    def __enter__(self):
        db_path = os.path.join(os.path.dirname(__file__), '../../instance/site.db')
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        return False

def db_connection(func):
    def wrapper(self, *args, **kwargs):
        with DBConnection() as cursor:
            result = func(self, cursor, *args, **kwargs)
            return result
    return wrapper

# ----- HASH PASSWORD ----- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ----- VERIFY PASSWORD ----- #
def verify_password(password, password_hash):
    """Verify a stored password against one provided by user"""
    return hash_password(password) == password_hash