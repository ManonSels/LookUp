import markdown
from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this!
    
    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import and register blueprints
    from app.routes.home import bp as home_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Add markdown filter
    @app.template_filter('markdown')
    def render_markdown(text):
        if not text:
            return ""
        # Convert markdown to HTML with code highlighting
        return markdown.markdown(
            text, 
            extensions=[
                'fenced_code',
                'tables',
                'toc'
            ]
        )
    
    return app

# User loader for Flask-Login
from app.models.user import UserModel

@login_manager.user_loader
def load_user(user_id):
    user_model = UserModel()
    return user_model.get_by_id(int(user_id))