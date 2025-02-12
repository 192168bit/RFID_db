from datetime import timedelta
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

from .config import config
from flask_jwt_extended import JWTManager

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_mode=None):
    app = Flask(__name__)
    CORS(app)
    config_mode = config_mode or os.getenv("CONFIG_MODE", "development")
    app.config.from_object(config[config_mode])
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_ALGORITHM"] = "HS256"       
    app.config["JWT_IDENTITY_CLAIM"] = "sub"
    app.config["JWT_CSRF_CHECK"] = False
    
    from src.seed_attribs import seed_attrib
    from src.seed_user import seed_users

    @app.cli.command("seed_attrib")
    def seed_attrib_command():
        """Seed the database with initial attributes."""
        with app.app_context():
            seed_attrib()
            
    @app.cli.command("seed_users")
    def seed_users_command():
        """Seed the database with initial attributes."""
        with app.app_context():
            seed_users()
            
    return app