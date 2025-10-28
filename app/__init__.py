from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# Add 'main.' prefix to the login_view
login_manager.login_view = 'main.login' 
login_manager.login_message_category = 'info' 

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import and register the blueprint
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Import models here so they are registered with Flask-Migrate
    from app import models 

    return app