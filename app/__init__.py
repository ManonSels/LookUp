import markdown
from flask import Flask
from flask_login import LoginManager
from app.models.user import UserModel
from datetime import datetime  # ADD THIS IMPORT

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this!
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.routes.home import bp as home_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.search import search_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(search_bp)
    
    @app.template_filter('markdown')
    def render_markdown(text):
        if not text:
            return ""
        
        return markdown.markdown(
            text, 
            extensions=[
                'fenced_code',
                'tables',
                'toc'
            ]
        )
    
    # ADD THE DATETIME FILTER INSIDE create_app FUNCTION
    @app.template_filter('datetime')
    def format_datetime(value):
        if not value:
            return ""
        
        # If it's a string, try to parse it
        if isinstance(value, str):
            try:
                # Handle SQLite datetime format
                if ' ' in value:
                    value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                else:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return value
        
        # Format as "MMM DD" (e.g., "Jan 15")
        if isinstance(value, datetime):
            return value.strftime('%b %d')
        
        return value
    
    return app

@login_manager.user_loader
def load_user(user_id):
    user_model = UserModel()
    return user_model.get_by_id(int(user_id))