import sqlite3
import os
from flask import g, current_app
from werkzeug.security import generate_password_hash, check_password_hash

# ----- DB CONNECTION ----- #
def get_db():
    """Get database connection for current request context"""
    if 'db' not in g:
        # Use instance folder for database
        instance_path = current_app.instance_path
        db_path = os.path.join(instance_path, 'site.db')
        
        # Ensure instance directory exists
        os.makedirs(instance_path, exist_ok=True)
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

class DBConnection:
    def __enter__(self):
        self.conn = get_db()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Commit changes and close connection for schema operations
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        return False

def db_connection(func):
    def wrapper(self, *args, **kwargs):
        with DBConnection() as cursor:
            result = func(self, cursor, *args, **kwargs)
            return result
    return wrapper

# ----- HASH PASSWORD ----- #
def hash_password(password):
    """Hash a password for storing"""
    return generate_password_hash(password)

# ----- VERIFY PASSWORD ----- #
def verify_password(password, password_hash):
    """Verify a stored password against one provided by user"""
    return check_password_hash(password_hash, password)