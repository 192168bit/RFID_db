from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from .config import config
import json

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config[config_mode])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    import src.users.models
    
    return app