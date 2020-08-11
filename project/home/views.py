from project import db
from project.models import User, Template
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
    templates_are_not_new = False
    templates_names = []

    if templates_are_not_new:
        Template.query.delete()  # delete existing templates in db
        templates = get_templates()  # return dictionary
        for template in templates.items():
            db_row = Template(*template)
            db.session.add(db_row)
        db.session.commit()
        templates_names = templates.keys()

    else:
        templates_db = Template.query.all()
        for template in templates_db:
            templates_names.append(template.name)

    form = NetworkDeviceForm(request.form)
    form.net_template.choices = list(templates_names)
    return render_template('home.html', form=form, error=error)


@home_blueprint.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

