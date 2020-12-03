from project import db
from project.models import Template, Network, Group, Tag, Device
from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user
from requests.exceptions import ConnectionError
from project.functions import get_templates, get_networks, get_devices, get_device, get_network
from project.admin.forms import GroupMembershipForm, GroupForm, ChoiceForm
from sqlalchemy.exc import OperationalError, ProgrammingError
import datetime, time
from project.decorators import *
from sqlalchemy import func
from project.logging import send_wr_log


# admin blueprint definition
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admin_blueprint.route('/users', methods=['GET', 'POST'])
@login_required
@is_admin
def admin_users():
    form = GroupMembershipForm(request.form)
    form.set_choices()

    return render_template('users.html', form=form)
    # load_templates_to_db()
    # load_networks_to_db()


@admin_blueprint.route('/groups', methods=['GET', 'POST'])
@login_required
@is_admin
def admin_groups():
    form = GroupForm(request.form, csrf_enabled=False)
    #form.set_choices()
    choice_form = ChoiceForm(request.form)
    choice_form.set_choices()

    if request.method == 'POST':
        if form.validate_on_submit():
            error = None
            #new_group_name = request.data.decode("utf-8")
            #new_group_name = new_group_name.strip()
            new_group_name = form.new_group_name.data.strip()
            if len(new_group_name) < 4:
                error = "Group name must be 4 characters long at least!"
                return jsonify(error)
            if Group.query.filter_by(name=new_group_name).first():
                error = "Exists!"
                return jsonify(error)
            new_group = Group(new_group_name)
            db.session.add(new_group)
            db.session.commit()
            log_msg = "User: {} - Group: {} is created.".format(current_user.username, new_group.name)
            send_wr_log(log_msg)
            return_data = [(group.id, group.name) for group in Group.query.all()]
            return jsonify(return_data)
        else:
            return jsonify(form.errors['new_group_name']), 400

    return render_template('groups.html', form=form, choice_form=choice_form)
    # load_templates_to_db()
    # load_networks_to_db()


@admin_blueprint.route('/groups/groups_select', methods=['GET'])
@login_required
@is_admin
def groups_select():
    return_data = [(group.id, group.name) for group in Group.query.all()]
    return jsonify(return_data)


@admin_blueprint.route('/networks', methods=['GET', 'POST'])
@login_required
@is_admin
def admin_networks():
    return render_template('networks.html')
    # load_templates_to_db()
    # load_networks_to_db()


@admin_blueprint.route('/networks/update_table', methods=['GET'])
@login_required
@is_admin
def update_admin_networks_table():
    '''
    If the network exists in db, updates the network row with new values;
     clears and rebuilds:
    - tags table,
    - networks-tags relations,
    - group-networks relations
    else, adds new network to networks table.
    :return: 200
    '''
    t1 = time.time()
    log_msg = "User: {} - Started updating networks table".format(current_user.username)
    send_wr_log(log_msg)
    try:
        meraki_networks = get_networks()
        templates = get_templates()
    except ConnectionError:
        error = "Meraki Server Bad Response"
        log_msg = "User: {} - {} while updating networks table.".format(current_user.username, error)
        send_wr_log(log_msg)
        return error
    for key, value in templates.items():
        template = Template.query.filter_by(meraki_id=value).first()
        if template:
            template.update(key, value)
        else:
            template = Template(key, value)
        db.session.add(template)
    db.session.commit()  # update templates table

    db_networks = Network.query.all()
    # cleaning non-existent networks from db table
    for network in db_networks:
        network_exists = False
        for m_network in meraki_networks:
            if m_network['meraki_id'] == network.meraki_id:
                network_exists = True
                break
        if not network_exists:
            log_msg = "User: {} - Network: {} with {} id does not exist on cloud; " \
                      "being deleted from db.".format(current_user.username, network.name, network.meraki_id)
            send_wr_log(log_msg)
            network.tags.clear()
            network.groups.clear()
            for device in network.devices:
                log_msg = "User: {} - Deleting device: {} related with network: {} " \
                          "from DB".format(current_user.username, device.serial, network.name)
                send_wr_log(log_msg)
                db.session.delete(device)
            db.session.delete(network)

    # networks from meraki cloud
    for network in meraki_networks:
        db_network = Network.query.filter_by(meraki_id=network['meraki_id']).first()
        # update if the network exists
        if db_network:
            db_network.update(**network)  # update the existing network in db consistent with cloud
            # update tags table and build their relation with networks
            if network['net_tags']:
                db_network.tags.clear()
                for tag in network['net_tags'].split(" "):
                    db_tag = Tag.query.filter_by(name=tag).first()
                    if db_tag:
                        db_network.tags.append(db_tag)
                    else:
                        new_tag = Tag(tag)
                        db.session.add(new_tag)
                        db_network.tags.append(new_tag)

        else:
            db_network = Network(**network)  # there is a new network on cloud, and save it in db

        db.session.add(db_network)
        db_network.committed = True  # db is synced with cloud

    db.session.commit()
    # build group network relation according to tag bindings to both networks and groups
    db_groups = Group.query.all()
    for db_group in db_groups:
        db_grp_tags = db_group.tags
        if db_grp_tags:
            for db_network in db_networks:
                db_net_tags = db_network.tags
                for db_net_tag in db_net_tags:
                    if db_net_tag in db_group.tags:
                        db_group.networks.append(db_network)
                        break
                    else:
                        if db_network in db_group.networks:
                            db_group.networks.remove(db_network)
                db.session.add(db_group)
    db.session.commit()

    # cleaning duplicate networks if not existing in cloud
#    sq = Network.query.with_entities(Network.name).group_by(Network.name).having(func.count(Network.name) > 1).subquery()
#    duplicates = Network.query.filter(Network.name == sq.c.name).order_by(Network.name).all()
#    if duplicates:
#        for network in duplicates:
#            result = get_network(network.meraki_id)
#            if result == 404:
#                network.groups.clear()
#                network.tags.clear()
#                if network.devices:
#                    for device in network.devices:
#                        db.session.delete(device)
#                db.session.delete(network)
#        db.session.commit()

    t2 = time.time()
    log_msg = "User: {} - Updating networks table is completed in {} seconds.".format(current_user.username, t2 - t1)
    send_wr_log(log_msg)
    return "success"


@admin_blueprint.route('/devices', methods=['GET'])
@login_required
@is_admin
def admin_devices():
    return render_template('devices.html')


@admin_blueprint.route('/devices/update_table', methods=['GET'])
@login_required
@is_admin
def admin_update_devices_table():
    t1 = time.time()
    log_msg = "User: {} - Started updating devices table.".format(current_user.username)
    send_wr_log(log_msg)
    try:
        reset_db_devices_table()
        # load_devices_to_db()
    except Exception as e:
        error = str(e)
        log_msg = "User: {} - {} while updating devices table.".format(current_user.username, error)
        send_wr_log(log_msg)
        return error
    t2 = time.time()
    log_msg = "User: {} - Updating devices table is completed in {} seconds.".format(current_user.username, t2 - t1)
    send_wr_log(log_msg)
    return "success"


def reset_db_devices_table():
    dev_status_list = get_devices()
    device_list = []
    number_of_rows = Device.query.delete()  # delete all table rows

    for device in dev_status_list:
        network = Network.query.filter_by(meraki_id=device['networkId']).first()
        dict_item = {'device_name': device['name'],
                     'device_serial': device['serial'],
                     'network_id': network.id,
                     'committed': True,
                     'status': device['status'],
                     'last_seen': device['lastReportedAt']
                     }
        device_list.append(Device(**dict_item))
    db.session.bulk_save_objects(device_list)
    db.session.commit()

    # another method to bulk insert
#    for device in dev_status_list:
#        network = Network.query.filter_by(meraki_id=device['networkId']).first()
#        dict_item = {'device_name': device['name'],
#                     'device_serial': device['serial'],
#                     'network_id': network.id,
#                     'committed': True,
#                     'status': device['status'],
#                     'last_seen': device['lastReportedAt']
#                     }
#        device_list.append(dict_item)
#
#    db.session.execute(Device.insert(), device_list)


def load_devices_to_db():
    db_changed = False
    dev_status_list = get_devices()
    for device in dev_status_list:
        db_device = Device.query.filter_by(serial=device['serial']).first()
        network = Network.query.filter_by(meraki_id=device['networkId']).first()
        if not db_device:  # new device
            dict_item = {'device_name': device['name'],
                         'device_serial': device['serial'],
                         'network_id': network.id,
                         'committed': True
                         }
            new_db_device = Device(**dict_item)
            db.session.add(new_db_device)
            db_changed = True
        else:  # check if the device is changed
            device_network_changed = db_device.network.meraki_id != device['networkId']
            device_name_changed = db_device.name != device['name']
            if device_name_changed or device_network_changed:
                dict_item = {'device_name': device['name'],
                             'device_serial': device['serial'],
                             'network_id': network.id,
                             'committed': True
                             }
                db_device.update(**dict_item)
                db.session.add(db_device)
                db_changed = True
    if db_changed:
        db.session.commit()


def load_templates_to_db():
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
            log_msg = "User: {} - {} while loading templates into db.".format(current_user.username, error)
            send_wr_log(log_msg)
            return error


def load_networks_to_db():
    if Network.query.first():
        network_age = datetime.datetime.now() - Network.query.first().reg_date
        network_age_days = network_age.days
    else:
        network_age_days = 100  # first time retrieving for template

    if network_age_days > 200:  # If templates in db are older than a week, then drop templates table and retrieve again
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
            log_msg = "User: {} - {} while loading networks into db.".format(current_user.username, error)
            send_wr_log(log_msg)
            return error
