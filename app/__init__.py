from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize extensions (not bound to app yet)
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # ==================================================
    # Configuration
    # ==================================================
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['PROFILE_UPLOAD_FOLDER'] = os.path.join(
        app.root_path, 'static/profile_pics'
    )
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ==================================================
    # Initialize Extensions
    # ==================================================
    db.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login to access this page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    # ==================================================
    # User Loader (Flask-Login)
    # ==================================================
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ==================================================
    # Register Blueprints
    # ==================================================
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # ==================================================
    # Create Database Tables Automatically
    # ==================================================
    with app.app_context():
        db.create_all()

    return app