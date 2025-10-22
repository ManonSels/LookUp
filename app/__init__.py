from flask import Flask
from flask_login import LoginManager
from app.models.schema import Schema
from app.models.user import UserModel

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-this'
    
    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Initialize database
    with app.app_context():
        schema = Schema()
        schema.init_db()
    
    # Register blueprints from routes package
    from app.routes import home_bp, auth_bp, admin_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app

@login_manager.user_loader
def load_user(user_id):
    user_model = UserModel()
    return user_model.get_by_id(user_id)