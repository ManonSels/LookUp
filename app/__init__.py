import os
import markdown
from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from app.models.user import UserModel
from datetime import datetime

login_manager = LoginManager()
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    cache.init_app(app)
    
    from app.routes.home import bp as home_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.search import search_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(search_bp)
    
    # Register teardown context
    from app.models.database import close_db
    app.teardown_appcontext(close_db)
    
    @app.template_filter('markdown')
    def render_markdown(text):
        if not text:
            return ""
        
        # Pre-process checkbox syntax [ ] and [x]
        if text:
            text = text.replace('[ ]', '<input type="checkbox" disabled>')
            text = text.replace('[x]', '<input type="checkbox" checked disabled>')
            text = text.replace('[X]', '<input type="checkbox" checked disabled>')
        
        # Use markdown with proper extensions
        html = markdown.markdown(
            text, 
            extensions=[
                'fenced_code',    # Code blocks
                'tables',         # Tables
                'toc',           # Table of contents
                'extra',         # Adds many features
                'nl2br',         # Convert newlines to <br>
                'sane_lists',    # Better list handling
            ]
        )
        
        return html
    
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
    try:
        user_model = UserModel()
        return user_model.get_by_id(int(user_id))
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error loading user {user_id}: {e}")
        return None