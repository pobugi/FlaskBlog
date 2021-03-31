import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
from flask_mail import Mail
from blog.config import Config


basedir = os.path.abspath(os.path.dirname(__file__)) #check
app = Flask(__name__)
app.config.from_object(Config)
# app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images/userpics')
photos = UploadSet('photos', IMAGES)

configure_uploads(app, photos)
patch_request_class(app)
db = SQLAlchemy(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




from .users import routes
from .posts import routes
from .admin import routes
from .errors import handlers