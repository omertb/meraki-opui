from project import db
from project.models import User, Template, Network, Device
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from project.home.forms import NetworkDeviceForm
from project.home.functions import get_templates
import datetime, json


# home blueprint definition
home_blueprint = Blueprint('home', __name__, template_folder='templates')


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


@home_blueprint.route('/device.json', methods=['GET', 'POST'])
@login_required
def device_table():
    if request.method == 'POST':
        selected_networks = request.form.to_dict()
        print(selected_networks)
        with open("selected_networks.json", "w", encoding='utf-8') as f:
            json.dump(selected_networks, f, ensure_ascii=False, indent=4)
        return selected_networks
    else:
        with open("selected_networks.json") as f:
            selected_networks = json.load(f)
        return selected_networks


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
        Template.query.delete()
        templates = get_templates()  # returns dictionary
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
    form.registered_nets.choices = [value for value, in user_networks.values(Network.name)]

    if request.method == 'POST':
        device_serials_list = form.serial_nos.data.strip().upper().replace(" ","").split("\r\n")

        if form.new_or_existing.data == 'existing':
            pass
        else:

            if form.net_type.data == 'firewall':
                pass
            else:
                net_name = form.net_name.data
                net_type = form.net_type.data
                user_id = current_user.id
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

    return render_template('home.html', form=form, error=error, user_networks=user_networks, devices_list=devices_list)


@home_blueprint.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

