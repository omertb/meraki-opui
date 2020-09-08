from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
# config
app.config.from_object('config.DevelopmentConfig')
# create the sqlalchemy object
db = SQLAlchemy(app)

# import blueprints
from project.users.views import users_blueprint
from project.home.views import home_blueprint
from project.json.views import json_blueprint
from project.admin.views import admin_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(json_blueprint)
app.register_blueprint(admin_blueprint)

from project.models import User

login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()
