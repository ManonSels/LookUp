from .database import db_connection

class Schema:
    @db_connection
    def create_tables(self, cursor):

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
        
        # ------------- TOPICS TABLE ------------- #
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category_id INTEGER NOT NULL,
                display_order INTEGER DEFAULT 0,
                is_published BOOLEAN DEFAULT 0,
                user_id INTEGER NOT NULL,
                card_color_light TEXT DEFAULT '#ffffff',
                card_color_dark TEXT DEFAULT '#1a1a1a',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (category_id) REFERENCES category (id)
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
                section_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES section (id) ON DELETE CASCADE
            )
        ''')
        
        print("Database tables created successfully!")
    
    # ----- CREATE ADMIN USER ----- #
    @db_connection
    def create_admin_user(self, cursor):
        from .database import hash_password
        
        cursor.execute('SELECT id FROM user WHERE username = ?', ('admin',))
        admin = cursor.fetchone()
        
        if not admin:
            password_hash = hash_password('admin123')
            cursor.execute(
                'INSERT INTO user (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                ('admin', 'admin@example.com', password_hash, 1)
            )
            print("Admin user created!")
    
    # ----- INITIALIZE ENTIRE DB ----- #
    def init_db(self):
        self.create_tables()
        self.create_admin_user()