# when importing website folder
# stuff here will run on startup
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    # secures cookies/session data related to website
    app.config['SECRET_KEY'] = 'sdkjfdkjf'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    db.init_app(app)    # which app we use for database

    # have blueprints that contain different views
    # tells flask where to locate URLs
    from .views import views
    from .auth import auth

    # define new URLs within auth using @auth.route(url)
    # (same for views)
    # any URL defined within views or auth will be prefixed by url_prefix
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

        # define classes before creating database
    from .models import User, Note

        # create database
    with app.app_context():
        db.create_all()
    

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'     # where to go if not logged in
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    return app

    # not used for now
def create_database(app):
        # check if database exists
        # if not, then create one
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created database')