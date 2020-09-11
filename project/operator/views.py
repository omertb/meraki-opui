from project import db
from project.models import Template, Network, Device, Tag
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from project.operator.forms import NewNetworkForm, AddDevicesForm
from project.decorators import *
import datetime
from requests.exceptions import ConnectionError


# home blueprint definition
operator_blueprint = Blueprint('operator', __name__, template_folder='templates')


@operator_blueprint.route('/operator/add_devices', methods=['GET', 'POST'])
@login_required
@is_operator
def add_devices():
    error = None
    form = AddDevicesForm(request.form)
    form.set_choices()
    form.serial_nos.data = ""
    if request.method == 'POST':
        form_dict = request.get_json()
        net_id = form_dict['network']
        devices = form_dict['devices']
        device_serials_list = devices.strip().upper().replace(" ", "").split("\n")
        error = save_devices_in_db(device_serials_list, int(net_id))
        return error

    return render_template('add_devices.html', current_user=current_user, form=form, error=error)


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

    form = NewNetworkForm(request.form)
    form.net_template.choices = list(templates_names)
    form.set_choices()
    #####
    # end of "on page load" block

    if request.method == 'POST':
        error = None
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
        network.net_tags = ""
        for tag_id in form.net_tag_mselect.data:
            tag = Tag.query.get(int(tag_id))
            network.tags.append(tag)
            network.net_tags += tag.name + " "
        # location specific tag for name seperated with dash;
        # eg. for network name AB11-Firewall, then new tag will be AB11
        if "-" in net_name:
            specific_tag_name = net_name.split("-")[0]
            specific_tag = Tag.query.filter_by(name=specific_tag_name).first()
            if not specific_tag:
                new_network_tag = Tag(specific_tag_name)
                db.session.add(new_network_tag)
                db.session.commit()
                network.tags.append(new_network_tag)
            else:
                network.tags.append(specific_tag)
        db.session.add(network)
        db.session.commit()

        return jsonify(error)

    return render_template('new_network.html', current_user=current_user, form=form, error=error)


def save_devices_in_db(device_serials_list, net_id):
    network = Network.query.get(net_id)
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
    if error:
        return jsonify(error)
    return jsonify("success")
