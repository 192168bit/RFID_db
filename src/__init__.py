from datetime import timedelta
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from .config import config
from flask_jwt_extended import JWTManager

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config[config_mode])
    

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_ALGORITHM"] = "HS256"       
    app.config["JWT_IDENTITY_CLAIM"] = "sub"
    app.config["JWT_CSRF_CHECK"] = False

    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    return app