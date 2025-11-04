from app import create_app
from app.models.schema import Schema
import os
from dotenv import load_dotenv

load_dotenv()

# Debug: Check if environment variables are loaded
print("Environment variables:")
print(f"ADMIN_USERNAME: {os.environ.get('ADMIN_USERNAME')}")
print(f"ADMIN_PASSWORD: {os.environ.get('ADMIN_PASSWORD')}")

app = create_app()

with app.app_context():
    try:
        schema = Schema()
        if schema.init_db():
            print("Database initialized successfully!")
        else:
            print("Error initializing database!")
    except Exception as e:
        print(f"Error during database initialization: {e}")

if __name__ == '__main__':
    app.run(debug=True)