from project import db
from project.models import User, Template, Network, Device
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from project.home.forms import NetworkDeviceForm
from project.home.functions import get_templates
import datetime
from requests.exceptions import ConnectionError


# home blueprint definition
home_blueprint = Blueprint('home', __name__, template_folder='templates')


@home_blueprint.route('/delete_networks', methods=['POST'])
@login_required
def delete_networks():
    result = []
    if request.method == 'POST':
        networks_to_be_deleted = request.get_json()
        print(networks_to_be_deleted)
        for network in networks_to_be_deleted:
            db_network = Network.query.filter_by(name=network['name']).first()
            related_devices = Device.query.filter_by(network_id=db_network.id)
            if related_devices:
                for device in related_devices:
                    db.session.delete(device)
                    result.append("Device: {} in Network: {} is deleted!".format(device.name, db_network.name))
            db.session.delete(db_network)
            result.append("Network: {} is deleted!".format(db_network.name))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)



@home_blueprint.route('/network.json', methods=['GET'])
@login_required
def network_table():
    user_networks = Network.query.filter_by(user_id=current_user.id)
    network_list = []
    for row, network in enumerate(user_networks.all()):
        network = network.serialize()
        network['rowNum'] = row + 1
        network_list.append(network)
    return jsonify(network_list)
    # return jsonify([network.serialize() for network in user_networks.all()])


@home_blueprint.route('/device.json', methods=['POST'])
@login_required
def device_table():
    if request.method == 'POST':
        selected_networks = request.get_json()
        device_list = []
        i = 1
        for network in selected_networks:
            network_devices = Device.query.filter_by(network_id=network['id'])
            for device in network_devices:
                device = device.serialize()
                device['rowNum'] = i
                device['network'] = network['name']
                device_list.append(device)
                i += 1
        return jsonify(device_list)
    else:
        return "Not Found", 404


@home_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    error = None
    template_age = datetime.datetime.now() - Template.query.first().reg_date
    templates_names = []
    user_networks = Network.query.filter_by(user_id=current_user.id)
    devices_list = []
    for network in user_networks:
        devices_list.extend(Device.query.filter_by(network_id=network.id))

    if template_age.days > 7:  # If templates in db are older than a week, then drop templates table and retrieve again
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

    if request.method == 'POST':
        device_serials_list = form.serial_nos.data.strip().upper().replace(" ", "").split("\r\n")
        print(form)

        if form.new_or_existing.data == 'existing':
            pass

        elif form.new_or_existing.data == 'new':
            net_name = form.net_name.data
            net_type = form.net_type.data
            user_id = current_user.id

            # ensure network name does not already exists
            network = Network.query.filter_by(name=net_name).first()
            if network:
                error = "Network already exists, try another unique name"
                # return render_template('home.html', form=form, error=error)
                return jsonify(error)

            error = None
            if net_type == 'firewall':
                pass
            else:
                network = Network(net_name, net_type, user_id)
                db.session.add(network)
                db.session.commit()
                network = Network.query.filter_by(name=net_name).first()
                for device_serial in device_serials_list:
                    dev_name = device_serial.replace("-", "")
                    dev_serial = device_serial
                    network_id = network.id
                    device = Device(dev_name, dev_serial, network_id)
                    db.session.add(device)
                db.session.commit()

        return jsonify(error)

    return render_template('home.html', form=form, error=error)


@home_blueprint.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

