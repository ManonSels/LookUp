import os
from .database import db_connection

class Schema:
    @db_connection
    def create_tables(self, cursor):
        try:
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

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS section (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    topic_id INTEGER NOT NULL,
                    FOREIGN KEY (topic_id) REFERENCES topic (id) ON DELETE CASCADE
                )
            ''')
            
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
            cursor.execute("PRAGMA table_info(topic)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            if 'category_id' in columns:
                print("Migrating existing category relationships...")
                
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
    
    @db_connection
    def create_admin_user(self, cursor):
        try:
            from .database import hash_password
            
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            cursor.execute('SELECT id FROM user WHERE username = ?', (admin_username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                password_hash = hash_password(admin_password)
                cursor.execute(
                    'UPDATE user SET password_hash = ?, is_admin = 1 WHERE username = ?',
                    (password_hash, admin_username)
                )
            else:
                password_hash = hash_password(admin_password)
                cursor.execute(
                    'INSERT INTO user (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                    (admin_username, f'{admin_username}@example.com', password_hash, 1)
                )
            
            return True
        except Exception as e:
            print(f"ERROR creating admin user: {e}")
            return False
    
    def init_db(self):
        try:
            if self.create_tables():
                self.migrate_existing_data()
                self.create_admin_user()
                print("Database initialized successfully!")
                return True
            return False
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False