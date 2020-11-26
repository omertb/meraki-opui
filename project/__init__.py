from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)
# config
app.config.from_object('config.DevelopmentConfig')
# create the sqlalchemy object
db = SQLAlchemy(app)
# {{ csrf_token() }} in jinja template
CSRFProtect(app)


# import blueprints
from project.users.views import users_blueprint
from project.operator.views import operator_blueprint
from project.json.views import json_blueprint
from project.admin.views import admin_blueprint
from project.models import User


app.register_blueprint(users_blueprint)
app.register_blueprint(operator_blueprint)
app.register_blueprint(json_blueprint)
app.register_blueprint(admin_blueprint)

# session header options:
#app.config.update(
#    SESSION_COOKIE_SECURE=False,
#    SESSION_COOKIE_HTTPONLY=True,
#    SESSION_COOKIE_SAMESITE='Lax',
#)

login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.alt_id == user_id).first()
