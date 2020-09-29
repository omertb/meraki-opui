from project import db
from project.models import Template, Network, Device, Tag
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from project.operator.forms import NewNetworkForm, AddDevicesForm
from project.decorators import *
from project.logging import send_wr_log
from sqlalchemy.exc import OperationalError, ProgrammingError
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
        device_serials_list = devices.strip().upper().replace(" ", "").replace("*", "-").split("\n")
        while '' in device_serials_list:
            device_serials_list.remove('')  # remove blank items
        error = save_devices_in_db(device_serials_list, int(net_id))
        log_msg = "User: {} - Saving devices in DB: {}".format(current_user.username, error)
        send_wr_log(log_msg)
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
    try:
        templates_db = Template.query.all()
    except (ProgrammingError, OperationalError) as e:
        error_log = str(e)
        log_msg = "Database error on (Get) New Network: {}".format(error_log)
        send_wr_log(log_msg)
        return jsonify("Database error!")
    for template in templates_db:
        templates_names.append(template.name)

    form = NewNetworkForm(request.form)
    form.net_template.choices = list(templates_names)
    form.set_choices()
    #####
    # end of "on page load" block

    if request.method == 'POST':
        net_will_be_copied = False
        error = None
        net_name = form.net_name.data
        net_name = net_name.strip()
        # validation on serverside
        if net_name == "":
            return jsonify("Enter a unique network name!")

        net_type = form.net_type.data
        user_id = current_user.id

        # ensure that network name does not already exist in db
        try:
            network = Network.query.filter_by(name=net_name).first()
        except (ProgrammingError, OperationalError) as e:
            error_log = str(e)
            log_msg = "Database error on (Post) New Network: {}".format(error_log)
            send_wr_log(log_msg)
            return jsonify("Database error!")
        if network:
            error = "Network already exists, try another unique name"
            # return render_template('home.html', form=form, error=error)
            log_msg = "User: {} - Network Name: {} - {}".format(current_user.username, network.name, error)
            send_wr_log(log_msg)
            return jsonify(error)

        if net_type == 'appliance':
            template = Template.query.filter_by(name=form.net_template.data).first()
            bound_template = template.meraki_id
            network = Network(net_name, net_type, user_id, bound_template=bound_template)
            log_msg = "User: {} - Network {} is being saved in DB" \
                      " with binding to template: {}".format(current_user.username, network.name, template.name)
            send_wr_log(log_msg)
        else:
            network_copy_source = Network.query.get(int(form.net_to_copy.data))
            source_network = network_copy_source.id  # it is not bound template, actually.
            network = Network(net_name, net_type, user_id, source_network=source_network)
            log_msg = "User: {} - Network {} is being saved in DB" \
                      " being copied from the Network: {}".format(current_user.username, network.name, source_network.name)
            send_wr_log(log_msg)

        network.net_tags = ""
        for tag_id in form.net_tag_mselect.data:
            tag = Tag.query.get(int(tag_id))
            network.tags.append(tag)
            network.net_tags += tag.name + " "
            # build network group relation according to selected tags
            for group in tag.groups:
                network.groups.append(group)
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
        log_msg = "User: {} - Network: {} is saved in DB with success".format(current_user.username, network.name)
        send_wr_log(log_msg)

        return jsonify(error)

    return render_template('new_network.html', current_user=current_user, form=form, error=error)


def save_devices_in_db(device_serials_list, net_id):
    error = []
    try:
        network = Network.query.get(net_id)
    except (ProgrammingError, OperationalError) as e:
        error_log = str(e)
        log_msg = "Database error on Add Devices: {}".format(error_log)
        send_wr_log(log_msg)
        return jsonify("Database error!")
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
        log_msg = "User: {} - Device Name: {}, Device Serial: {} is saved in DB".format(current_user.username, dev_name,
                                                                                        dev_serial)
        send_wr_log(log_msg)
    db.session.commit()
    if error:
        return jsonify(error)
    return jsonify("success")
