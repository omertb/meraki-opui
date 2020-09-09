from project import db
from project.models import Template, Network, Device
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from project.operator.forms import NetworkDeviceForm
from project.decorators import *
import datetime
from requests.exceptions import ConnectionError


# home blueprint definition
operator_blueprint = Blueprint('operator', __name__, template_folder='templates')


@operator_blueprint.route('/operator/new_network', methods=['GET', 'POST'])
@login_required
@is_operator
def new_network():
    error = None
    # beginning of "on page load"
    #####
    templates_names = []
    templates_db = Template.query.all()
    for template in templates_db:
        templates_names.append(template.name)

    form = NetworkDeviceForm(request.form)
    form.net_template.choices = list(templates_names)
    form.set_choices()
    user_networks = Network.query.filter_by(user_id=current_user.id)
    form.registered_nets.choices = [value for value, in user_networks.values(Network.name)]
    user_groups = current_user.groups
    for user_group in user_groups:
        if user_group.networks:
            group_networks = user_group.networks
            form.registered_nets.choices.extend([network.name for network in group_networks])
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

            if net_type == 'appliance':
                template = Template.query.filter_by(name=form.net_template.data).first()
                bound_template = template.meraki_id
            else:
                bound_template = None

            network = Network(net_name, net_type, user_id, bound_template=bound_template)
            db.session.add(network)
            db.session.commit()
        else:
            return jsonify("Bad option sent to server")

        error = save_devices_in_db(device_serials_list, net_name)

        return jsonify(error)

    return render_template('new_network.html', current_user=current_user, form=form, error=error)


def save_devices_in_db(device_serials_list, net_name):
    network = Network.query.filter_by(name=net_name).first()
    error = []
    for device_serial in device_serials_list:
        dev_name = device_serial.replace("-", "")
        dev_serial = device_serial
        network_id = network.id
        device = Device.query.filter_by(serial=device_serial).first()
        if device:
            error.append("Device with serial: {} already exists!".format(dev_serial))
            continue
        device = Device(dev_name, dev_serial, network_id)
        db.session.add(device)
    db.session.commit()
    if not len(error):
        return None
    return error
