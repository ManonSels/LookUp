from app import create_app
from app.models.schema import Schema

app = create_app()

# Initialize database on startup
with app.app_context():
    schema = Schema()
    schema.init_db()
    print("Database initialized!")

if __name__ == '__main__':
    app.run(debug=True)