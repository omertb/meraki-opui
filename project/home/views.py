from project import db
from project.models import User
from flask import render_template, Blueprint
from flask_login import login_required

# home blueprint definition
home_blueprint = Blueprint('home', __name__, template_folder='templates')


@home_blueprint.route('/')
@login_required
def home():
    # return "Hello, World!"  # return a string
    posts = db.session.query(User).all()
    return render_template('home.html', posts=posts)  # render a template


@home_blueprint.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

