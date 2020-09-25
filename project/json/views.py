from project import db
from project.models import Network, Device, Template, User, Group, Tag
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from project.decorators import *
from project.functions import create_network, bind_template, claim_network_devices, rename_device_v0
from requests.exceptions import ConnectionError


# home blueprint definition
json_blueprint = Blueprint('json', __name__, template_folder='templates')


'''administrator functions
to do:
- decorator for access by only admin users
'''


@json_blueprint.route('/users/users.json', methods=['GET'])
@login_required
@is_admin
def users_table():
    users = User.query.all()
    users_list = []
    for i, row in enumerate(users):
        user = {'name': row.username,
                'groups': [group.name for group in row.groups],
                'rowNum': i + 1,
                'admin': 'Yes' if row.admin else 'No',
                'operator': 'Yes' if row.operator else 'No'
                }
        users_list.append(user)
    return jsonify(users_list)


@json_blueprint.route('/users/user_operator', methods=['POST'])
@login_required
@is_admin
def negate_user_operator_access():
    if request.method == 'POST':
        users_to_be_negated = request.get_json()
        print(users_to_be_negated)
        for user in users_to_be_negated:
            if user['name'] == current_user.username:
                return jsonify("Cannot modify current user")
            db_user = User.query.filter_by(username=user['name']).first()
            # group = Group.query.filter_by(name='operators').first()
            db_user.operator = not db_user.operator
            # db_user.groups.append(group) if db_user.operator else db_user.groups.remove(group)
            db.session.add(db_user)
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
    return jsonify("success")


@json_blueprint.route('/users/user_admin', methods=['POST'])
@login_required
@is_admin
def negate_user_admin_access():
    if request.method == 'POST':
        users_to_be_negated = request.get_json()
        for user in users_to_be_negated:
            if user['name'] == current_user.username:
                return jsonify("Cannot modify current user")
            db_user = User.query.filter_by(username=user['name']).first()
            # group = Group.query.filter_by(name='administrators').first()
            db_user.admin = not db_user.admin
            # db_user.groups.append(group) if db_user.admin else db_user.groups.remove(group)
            db.session.add(db_user)
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
    return jsonify("success")


@json_blueprint.route('/users/reset_membership', methods=['POST'])
@login_required
@is_admin
def reset_membership():
    result = []
    if request.method == 'POST':
        users_to_be_reset = request.get_json()
        if users_to_be_reset:
            for user in users_to_be_reset:
                if user['name'] == current_user.username:
                    return jsonify("Cannot modify current user")
                db_user = User.query.filter_by(username=user['name']).first()
                db_user.groups.clear()
                db.session.add(db_user)
                result.append("User: {} groups have been reset!".format(db_user.username))
            try:
                db.session.commit()
                result.append("DB Write is successful!")
            except:
                return jsonify("Database error!")
    return jsonify(result)


@json_blueprint.route('/groups/groups.json', methods=['GET'])
@login_required
@is_admin
def groups_table():
    groups = Group.query.all()
    groups_list = []
    for i, row in enumerate(groups):
        group = {'rowNum': i + 1,
                 'name': row.name,
                 'users': [user.username for user in row.users],
                 'tags': [tag.name for tag in row.tags]
                 }
        groups_list.append(group)
    return jsonify(groups_list)


@json_blueprint.route('/groups/add_user', methods=['POST'])
@login_required
@is_admin
def add_user():
    result = []
    if request.method == 'POST':
        user_group_list = request.get_json()
        user_list = user_group_list[0]
        group_list = user_group_list[-1]
        for user_id in user_list:
            user = User.query.get(int(user_id))
            for grp_id in group_list:
                group = Group.query.get(int(grp_id))
                user.groups.append(group)
            db.session.add(user)
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/groups/reset_groups', methods=['POST'])
@login_required
@is_admin
def reset_groups():
    result = []
    if request.method == 'POST':
        groups_to_be_reset = request.get_json()
        for group in groups_to_be_reset:
            db_group = Group.query.filter_by(name=group['name']).first()
            # db_group.users.clear() # user relations are to be deleted in users section
            db_group.tags.clear()
            db_group.networks.clear()
            db.session.add(db_group)
            result.append("Group: {} tag and network relations are reset.\n"
                          "Please \'Update Networks\' in Networks page.".format(group['name']))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/groups/delete_groups', methods=['POST'])
@login_required
@is_admin
def delete_groups():
    result = []
    if request.method == 'POST':
        groups_to_be_deleted = request.get_json()
        for group in groups_to_be_deleted:
            db_group = Group.query.filter_by(name=group['name']).first()
            db.session.delete(db_group)
            result.append("Group: {} is removed".format(group['name']))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/networks/tag_group', methods=['POST'])
@login_required
@is_admin
def tag_group():
    result = []
    if request.method == 'POST':
        group_tag_list = request.get_json()
        group_list = group_tag_list[0]
        tag_list = group_tag_list[-1]
        for group_id in group_list:
            group = Group.query.get(int(group_id))
            for tag_id in tag_list:
                tag = Tag.query.get(int(tag_id))
                group.tags.append(tag)
            db.session.add(group)
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/networks/networks.json', methods=['GET'])
@login_required
@is_admin
def networks_table():
    networks = Network.query.all()
    networks_list = []
    for i, row in enumerate(networks):
        network = {'name': row.name,
                   'groups': [group.name for group in row.groups],
                   'tags': row.net_tags,
                   'rowNum': i + 1
                   }
        networks_list.append(network)
    return jsonify(networks_list)


@json_blueprint.route('/devices/devices.json', methods=['GET'])
@login_required
@is_admin
def devices_table():
    devices = Device.query.all()
    devices_list = []
    for i, row in enumerate(devices):
        device = {'rowNum': i + 1,
                  'name': row.name,
                  'serial': row.serial,
                  'device_model': row.devmodel,
                  'committed': "Yes" if row.committed else "No",
                  'network_name': row.network.name
                  }
        devices_list.append(device)
    return jsonify(devices_list)


'''user related functions
to do:
- update these functions so that posted networks or devices cannot be deleted on which current user is not authorized.
'''


@json_blueprint.route('/operator/delete_devices', methods=['POST'])
@login_required
@is_operator
def delete_devices():
    result = []
    if request.method == 'POST':
        devices_to_be_deleted = request.get_json()
        for device in devices_to_be_deleted:
            db_device = Device.query.filter_by(name=device['name']).first()
            network_name = db_device.network
            if db_device.committed:
                result.append("Device: {} in Network: {} cannot be deleted; "
                              "it is committed!".format(device['name'], network_name))
            else:
                db.session.delete(db_device)
                result.append("Device: {} is removed from Network: {}!".format(device['name'], network_name))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/operator/delete_networks', methods=['POST'])
@login_required
@is_operator
def delete_networks():
    result = []
    if request.method == 'POST':
        networks_to_be_deleted = request.get_json()
        for network in networks_to_be_deleted:
            db_network = Network.query.filter_by(name=network['name']).first()
            related_devices = Device.query.filter_by(network_id=db_network.id)
            if related_devices:
                for device in related_devices:
                    if device.committed:
                        result.append("Device: {} from Network: {} cannot be deleted; "
                                      "it is committed!".format(device.name, db_network.name))
                    else:
                        db.session.delete(device)
                        result.append("Device: {} from Network: {} is deleted!".format(device.name, db_network.name))
            if db_network.committed:
                result.append("Network: {} cannot be deleted; it is committed!".format(db_network.name))
            else:
                db.session.delete(db_network)
                result.append("Network: {} is deleted!".format(db_network.name))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/operator/network.json', methods=['GET'])
@login_required
@is_operator
def network_table():
    initial_query_list = []
    user_networks = Network.query.filter_by(user_id=current_user.id)
    initial_query_list.extend(user_networks)
    user_groups = current_user.groups
    for group in user_groups:
        initial_query_list.extend(group.networks)

    query_list = list(set(initial_query_list))

    network_list = []
    for row, network in enumerate(query_list):
        template_name = network.template.name if network.bound_template else None
        network = network.serialize()
        network['rowNum'] = row + 1
        network['committed'] = 'No' if network['committed'] is False else 'Yes'
        network['bound_template'] = template_name
        network_list.append(network)
    return jsonify(network_list)
    # return jsonify([network.serialize() for network in user_networks.all()])


@json_blueprint.route('/operator/device.json', methods=['POST'])
@login_required
@is_operator
def device_table():
    if request.method == 'POST':
        network_id = request.get_json()
        device_list = []
        i = 1
        network_devices = Device.query.filter_by(network_id=int(network_id))
        for device in network_devices:
            device_model = device.devmodel
            device = device.serialize()
            device['rowNum'] = i
            device['model'] = device_model
            device['committed'] = 'No' if device['committed'] is False else 'Yes'
            device_list.append(device)
            i += 1
        return jsonify(device_list)
    else:
        return "Not Found", 404


@json_blueprint.route('/operator/commit_networks', methods=['POST'])
@login_required
@is_operator
def commit_networks():
    result = []
    if request.method == 'POST':
        networks_to_be_commit = request.get_json()
        for network in networks_to_be_commit:
            db_network = Network.query.filter_by(name=network['name']).first()
            network_dict = {
                'name': db_network.name,
                'productTypes': [db_network.type],
                'tags': [tag.name for tag in db_network.tags]
            }
            try:
                # commit to cloud
                create_net_res = create_network(network_dict)
                # write new network meraki id to db
                db_network.meraki_id = create_net_res['id']
                db.session.add(db_network)
                # bind template
                if db_network.template:
                    template_meraki_id = db_network.template.meraki_id
                    bind_template(db_network.meraki_id, template_meraki_id)
                result.append("Network: {} committed to Meraki Cloud".format(db_network.name))
                db_network.committed = True
            except ConnectionError:
                result.append("Meraki Response Error for Network: {}".format(db_network.name))
                db_network.committed = False
        db.session.commit()
        return jsonify(result)


@json_blueprint.route('/operator/commit_devices', methods=['POST'])
@login_required
@is_operator
def commit_devices():
    result = []
    if request.method == 'POST':
        devices_to_be_commit = request.get_json()
        meraki_net_id_list = []
        dev_serial_list = []
        for i, device in enumerate(devices_to_be_commit):
            db_device = Device.query.filter_by(serial=device['serial']).first()
            # check if there is a mismatch in network ids of devices
            meraki_net_id_list.append(db_device.network.meraki_id)
            if i > 0:
                if meraki_net_id_list[i] != meraki_net_id_list[i-1]:
                    return jsonify("Error, there is mismatch between network ids")
            dev_serial_list.append(device['serial'])

        try:
            # bind devices to network on cloud
            response = claim_network_devices(meraki_net_id_list[0], dev_serial_list)
            if response == "success":
                result.append("Devices are claimed and bound to network")
            else:
                result.extend(response['errors'])

            # rename devices and get the model name from response and then update the table.
            for device in devices_to_be_commit:
                db_device = Device.query.filter_by(serial=device['serial']).first()
                meraki_net_id = db_device.network.meraki_id
                rename_response = rename_device_v0(meraki_net_id, device['serial'], device['name'])
                db_device.devmodel = rename_response['model']
                db_device.committed = True
                db.session.add(db_device)
            db.session.commit()

        except ConnectionError:
            result.append("Meraki Response Error")

        return jsonify(result)


@json_blueprint.route('/operator/rename_devices', methods=['POST'])
@login_required
@is_operator
def rename_devices():
    result = []
    if request.method == 'POST':
        rename_devices_json = request.get_json()
        device_name = rename_devices_json["device_name"]
        device_list = rename_devices_json["device_list"]
        for device in device_list:
            db_device = Device.query.filter_by(serial=device['serial']).first()
            meraki_net_id = db_device.network.meraki_id
            serial = db_device.serial
            try:
                rename_response = rename_device_v0(meraki_net_id, serial, device_name)
                result.append("{} with model {} is renamed to {}".format(db_device.name, rename_response['model'],
                                                                         device_name))
                db_device.name = device_name
                db_device.devmodel = rename_response['model']
                db.session.add(db_device)
            except ConnectionError:
                result.append("Meraki response error while renaming device: {}".format(device['name']))
        db.session.commit()
    return jsonify(result)
