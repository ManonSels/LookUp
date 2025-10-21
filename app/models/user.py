from flask_login import UserMixin
from .database import db_connection, verify_password

class UserModel(UserMixin):
    @db_connection
    def get_by_id(self, cursor, user_id):
        cursor.execute('SELECT * FROM user WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return None
        
        return self._dict_to_user(user_data)
    
    @db_connection
    def get_by_username(self, cursor, username):
        cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return None
        
        return self._dict_to_user(user_data)
    
    @db_connection
    def create_user(self, cursor, username, email, password, is_admin=False):
        from .database import hash_password
        password_hash = hash_password(password)
        
        try:
            cursor.execute(
                'INSERT INTO user (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, 1 if is_admin else 0)
            )
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @db_connection
    def get_all_users(self, cursor):
        cursor.execute('SELECT * FROM user ORDER BY username')
        users_data = cursor.fetchall()
        return [self._dict_to_user(user) for user in users_data]
    
    def _dict_to_user(self, user_data):
        """Convert database row to User object"""
        user = UserModel()
        user.id = user_data['id']
        user.username = user_data['username']
        user.email = user_data['email']
        user.password_hash = user_data['password_hash']
        user.is_admin = bool(user_data['is_admin'])
        user.created_at = user_data['created_at']
        return user
    
    def check_password(self, password):
        return verify_password(password, self.password_hash)