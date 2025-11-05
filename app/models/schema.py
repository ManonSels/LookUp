import os
from flask import current_app
from .database import db_connection, get_db, close_db

class Schema:
    @db_connection
    def create_tables(self, cursor):
        try:
            # ------------- USERS TABLE ------------- #
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # ------------- CATEGORY TABLE ------------- #
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ------------- TOPICS TABLE (UPDATED - NO CATEGORY_ID) ------------- #
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    display_order INTEGER DEFAULT 0,
                    is_published BOOLEAN DEFAULT 0,
                    user_id INTEGER NOT NULL,
                    card_color_light TEXT DEFAULT '#ffffff',
                    card_color_dark TEXT DEFAULT '#1a1a1a',
                    logo_filename_light TEXT,
                    logo_filename_dark TEXT,
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id)
                )
            ''')
            
            # ------------- TOPIC_CATEGORY JUNCTION TABLE ------------- #
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topic_category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (topic_id) REFERENCES topic (id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE CASCADE,
                    UNIQUE(topic_id, category_id)
                )
            ''')
            
            # ------------- SECTIONS TABLE ------------- #
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS section (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    topic_id INTEGER NOT NULL,
                    FOREIGN KEY (topic_id) REFERENCES topic (id) ON DELETE CASCADE
                )
            ''')
            
            # ------------- SECTIONS ITEMS TABLE ------------- #
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS section_item (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    markdown_content TEXT NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    card_size TEXT DEFAULT 'normal',
                    bookmark_color TEXT DEFAULT '#3b82f6',
                    section_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (section_id) REFERENCES section (id) ON DELETE CASCADE
                )
            ''')
            
            print("Database tables created successfully!")
            return True
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
    
    @db_connection
    def migrate_existing_data(self, cursor):
        """Migrate existing topic.category_id to topic_category table"""
        try:
            # Check if topic table has category_id column (old structure)
            cursor.execute("PRAGMA table_info(topic)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            if 'category_id' in columns:
                print("Migrating existing category relationships...")
                
                # Copy existing category relationships to topic_category table
                cursor.execute('''
                    INSERT INTO topic_category (topic_id, category_id, display_order)
                    SELECT id, category_id, display_order FROM topic 
                    WHERE category_id IS NOT NULL
                ''')
                
                print("Existing data migrated successfully!")
            return True
        except Exception as e:
            print(f"Error migrating existing data: {e}")
            return False
    
    # ----- CREATE ADMIN USER ----- #
    @db_connection
    def create_admin_user(self, cursor):
        try:
            from .database import hash_password
            
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            print(f"DEBUG: Creating admin user - Username: '{admin_username}', Password: '{admin_password}'")
            
            # Check if user exists
            cursor.execute('SELECT id FROM user WHERE username = ?', (admin_username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                print(f"DEBUG: User '{admin_username}' already exists with ID: {existing_user['id']}")
                # Update the password to use the new hashing
                password_hash = hash_password(admin_password)
                cursor.execute(
                    'UPDATE user SET password_hash = ?, is_admin = 1 WHERE username = ?',
                    (password_hash, admin_username)
                )
                print(f"DEBUG: Updated password for existing user '{admin_username}'")
            else:
                # Create new admin user
                password_hash = hash_password(admin_password)
                cursor.execute(
                    'INSERT INTO user (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                    (admin_username, f'{admin_username}@example.com', password_hash, 1)
                )
                print(f"DEBUG: Created new admin user '{admin_username}'")
            
            # Verify the user was created/updated
            cursor.execute('SELECT id, username, password_hash FROM user WHERE username = ?', (admin_username,))
            verified_user = cursor.fetchone()
            if verified_user:
                print(f"DEBUG: Verified - User ID: {verified_user['id']}, Username: {verified_user['username']}")
                print(f"DEBUG: Password hash: {verified_user['password_hash'][:50]}...")
            else:
                print("DEBUG: ERROR - User verification failed!")
                
            return True
        except Exception as e:
            print(f"ERROR creating admin user: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ----- INITIALIZE ENTIRE DB ----- #
    def init_db(self):
        try:
            if self.create_tables():
                self.migrate_existing_data()  # Migrate existing data
                self.create_admin_user()
                print("Database initialized successfully!")
                return True
            return False
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False