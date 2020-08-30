from project import db
from project.models import Template, Network, Device
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from requests.exceptions import ConnectionError
from project.functions import get_templates, get_networks
import datetime


# admin blueprint definition
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admin_blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    error = None
    if Template.query.first():
        template_age = datetime.datetime.now() - Template.query.first().reg_date
        template_age_days = template_age.days
    else:
        template_age_days = 100  # first time retrieving for template

    if template_age_days > 7:  # If templates in db are older than a week, then drop templates table and retrieve again
        try:
            templates = get_templates()  # returns dictionary
            Template.query.delete()
            for template in templates.items():
                db_row = Template(*template)
                db.session.add(db_row)
            db.session.commit()
        except ConnectionError:
            error = "Meraki Server Bad Response"
            return error

    if Network.query.first():
        network_age = datetime.datetime.now() - Network.query.first().reg_date
        network_age_days = network_age.days
    else:
        network_age_days = 100  # first time retrieving for template

    if network_age_days > 30:  # If templates in db are older than a week, then drop templates table and retrieve again
        try:
            networks = get_networks()  # returns dictionary list
            Network.query.delete()
            for network in networks:
                db_row = Network(**network)
                db.session.add(db_row)
            db.session.commit()
            return "Networks are saved in db"
        except ConnectionError:
            error = "Meraki Server Bad Response"
            return error
