from project import db
from project.models import User
from flask import render_template, Blueprint, request
from flask_login import login_required
from project.home.forms import NetworkDeviceForm
from project.home.functions import get_templates

# home blueprint definition
home_blueprint = Blueprint('home', __name__, template_folder='templates')


@home_blueprint.route('/')
@login_required
def home():
    error = None
    templates_are_not_new = True
    if templates_are_not_new:
        templates_names = get_templates().keys()
    form = NetworkDeviceForm(request.form)
    form.net_template.choices = list(templates_names)
    return render_template('home.html', form=form, error=error)


@home_blueprint.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

