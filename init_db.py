import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.models.schema import Schema

def init_database():
    print("Initializing database...")
    schema = Schema()
    schema.init_db()
    print("Database tables created successfully!")
    print("Admin user created: username='admin', password='admin123'")

if __name__ == '__main__':
    init_database()