from project import db
from project.models import Template, Network, Device
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from project.home.forms import NetworkDeviceForm
from project.home.functions import get_templates
import datetime
from requests.exceptions import ConnectionError


# home blueprint definition
home_blueprint = Blueprint('home', __name__, template_folder='templates')


@home_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # beginning of "on page load"
    #####
    error = None
    if Template.query.first():
        template_age = datetime.datetime.now() - Template.query.first().reg_date
        template_age_days = template_age.days
    else:
        template_age_days = 100  # first time retrieving for template
    templates_names = []
    user_networks = Network.query.filter_by(user_id=current_user.id)
    devices_list = []
    for network in user_networks:
        devices_list.extend(Device.query.filter_by(network_id=network.id))

    if template_age_days > 7:  # If templates in db are older than a week, then drop templates table and retrieve again
        try:
            templates = get_templates()  # returns dictionary
            Template.query.delete()
            for template in templates.items():
                db_row = Template(*template)
                db.session.add(db_row)
            db.session.commit()
            templates_names = templates.keys()
        except ConnectionError:
            error = "Meraki Server Bad Response"

    else:  # if templates are not older than the value above, then use the ones in DB
        templates_db = Template.query.all()
        for template in templates_db:
            templates_names.append(template.name)

    form = NetworkDeviceForm(request.form)
    form.net_template.choices = list(templates_names)
    form.registered_nets.choices = [value for value, in user_networks.values(Network.name)]
    #####
    # end of "on page load" block

    if request.method == 'POST':
        error = None
        device_serials_list = form.serial_nos.data.strip().upper().replace(" ", "").split("\r\n")

        if form.new_or_existing.data == 'existing':
            net_name = form.registered_nets.data

        elif form.new_or_existing.data == 'new':
            net_name = form.net_name.data
            # validation on serverside
            if net_name == "":
                return jsonify("Enter a unique network name!")

            net_type = form.net_type.data
            user_id = current_user.id

            # ensure that network name does not already exist in db641296
            network = Network.query.filter_by(name=net_name).first()
            if network:
                error = "Network already exists, try another unique name"
                # return render_template('home.html', form=form, error=error)
                return jsonify(error)

            if net_type == 'firewall':
                template = Template.query.filter_by(name=form.net_template.data).first()
                bound_template = template.id
            else:
                bound_template = None

            network = Network(net_name, net_type, user_id, bound_template)
            db.session.add(network)
            db.session.commit()
        else:
            return jsonify("Bad option sent to server")

        save_devices_in_db(device_serials_list, net_name)

        return jsonify(error)

    return render_template('home.html', form=form, error=error)


def save_devices_in_db(device_serials_list, net_name):
    network = Network.query.filter_by(name=net_name).first()
    for device_serial in device_serials_list:
        dev_name = device_serial.replace("-", "")
        dev_serial = device_serial
        network_id = network.id
        device = Device(dev_name, dev_serial, network_id)
        db.session.add(device)
    db.session.commit()
