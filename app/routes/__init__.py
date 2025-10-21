from .home import bp as home_bp
from .auth import auth_bp
from .admin import admin_bp

# This makes the blueprints available to the main app
__all__ = ['home_bp', 'auth_bp', 'admin_bp']