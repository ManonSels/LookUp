from flask_login import UserMixin
from .database import db_connection, verify_password
from flask import current_app

class UserModel(UserMixin):
    # ----- BY ID ----- #
    @db_connection
    def get_by_id(self, cursor, user_id):
        try:
            cursor.execute('SELECT * FROM user WHERE id = ?', (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return None
            
            return self._dict_to_user(user_data)
        except Exception as e:
            current_app.logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    # ----- BY USERNAME ----- #
    @db_connection
    def get_by_username(self, cursor, username):
        try:
            cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return None
            
            return self._dict_to_user(user_data)
        except Exception as e:
            current_app.logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    # ----- CREATE USER ----- #
    @db_connection
    def create_user(self, cursor, username, email, password, is_admin=False):
        try:
            from .database import hash_password
            
            # Validate inputs
            if not username or not email or not password:
                raise ValueError("Username, email, and password are required")
            
            if len(username) > 50 or len(email) > 100:
                raise ValueError("Username or email too long")
            
            password_hash = hash_password(password)
            
            cursor.execute(
                'INSERT INTO user (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, 1 if is_admin else 0)
            )
            return cursor.lastrowid
        except Exception as e:
            current_app.logger.error(f"Error creating user: {e}")
            return None
    
    # ----- ALL USERS ----- #
    @db_connection
    def get_all_users(self, cursor):
        try:
            cursor.execute('SELECT * FROM user ORDER BY username')
            users_data = cursor.fetchall()
            return [self._dict_to_user(user) for user in users_data]
        except Exception as e:
            current_app.logger.error(f"Error getting all users: {e}")
            return []
    
    # ----- CHECK PASSWORD ----- #
    def check_password(self, password):
        try:
            return verify_password(password, self.password_hash)
        except Exception as e:
            current_app.logger.error(f"Error checking password: {e}")
            return False
        
        
    
    # ----- CONVERT DB ROW TO USER OBJECT ----- #
    def _dict_to_user(self, user_data):
        user = UserModel()
        user.id = user_data['id']
        user.username = user_data['username']
        user.email = user_data['email']
        user.password_hash = user_data['password_hash']
        user.is_admin = bool(user_data['is_admin'])
        user.created_at = user_data['created_at']
        return user