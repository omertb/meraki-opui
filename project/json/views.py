from project import db
from project.models import Network, Device, Template, User, Group, Tag
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user


# home blueprint definition
json_blueprint = Blueprint('json', __name__, template_folder='templates')


@json_blueprint.route('/networks/tag_group', methods=['POST'])
@login_required
def tag_group():
    result = []
    if request.method == 'POST':
        group_tag_list = request.get_json()
        print(group_tag_list)
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


@json_blueprint.route('/groups/add_user', methods=['POST'])
@login_required
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
def reset_groups():
    result = []
    if request.method == 'POST':
        groups_to_be_reset = request.get_json()
        for group in groups_to_be_reset:
            db_group = Group.query.filter_by(name=group['name']).first()
            db_group.users.clear()
            db.session.add(db_group)
            result.append("Group: {} membership is reset".format(group['name']))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/groups/delete_groups', methods=['POST'])
@login_required
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


@json_blueprint.route('/delete_devices', methods=['POST'])
@login_required
def delete_devices():
    result = []
    if request.method == 'POST':
        devices_to_be_deleted = request.get_json()
        for device in devices_to_be_deleted:
            db_device = Device.query.filter_by(name=device['name']).first()
            network_name = device['network']
            db.session.delete(db_device)
            result.append("Device: {} is removed from Network: {}!".format(device['name'], network_name))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/delete_networks', methods=['POST'])
@login_required
def delete_networks():
    result = []
    if request.method == 'POST':
        networks_to_be_deleted = request.get_json()
        for network in networks_to_be_deleted:
            db_network = Network.query.filter_by(name=network['name']).first()
            related_devices = Device.query.filter_by(network_id=db_network.id)
            if related_devices:
                for device in related_devices:
                    db.session.delete(device)
                    result.append("Device: {} from Network: {} is deleted!".format(device.name, db_network.name))
            db.session.delete(db_network)
            result.append("Network: {} is deleted!".format(db_network.name))
        try:
            db.session.commit()
        except:
            return jsonify("Database error!")
        return jsonify(result)


@json_blueprint.route('/network.json', methods=['GET'])
@login_required
def network_table():
    user_networks = Network.query.filter_by(user_id=current_user.id)
    network_list = []
    for row, network in enumerate(user_networks.all()):
        template_name = network.template.name if network.template else None
        network = network.serialize()
        network['rowNum'] = row + 1
        network['committed'] = 'No' if network['committed'] is False else 'Yes'
        network['bound_template'] = template_name
        network_list.append(network)
    return jsonify(network_list)
    # return jsonify([network.serialize() for network in user_networks.all()])


@json_blueprint.route('/device.json', methods=['POST'])
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
                device['committed'] = 'No' if device['committed'] is False else 'Yes'
                device_list.append(device)
                i += 1
        return jsonify(device_list)
    else:
        return "Not Found", 404


@json_blueprint.route('/users/users.json', methods=['GET'])
@login_required
def users_table():
    users = User.query.all()
    users_list = []
    for i, row in enumerate(users):
        user = {'name': row.username,
                'groups': [group.name for group in row.groups],
                'rowNum': i + 1,
                'admin': 'Yes' if row.admin else 'No',
                'operator': 'Yes' if row.verified else 'No'
                }
        users_list.append(user)
    return jsonify(users_list)


@json_blueprint.route('/groups/groups.json', methods=['GET'])
@login_required
def groups_table():
    groups = Group.query.all()
    groups_list = []
    for i, row in enumerate(groups):
        group = {'name': row.name,
                'users': [user.username for user in row.users],
                'rowNum': i + 1
                }
        groups_list.append(group)
    return jsonify(groups_list)


@json_blueprint.route('/networks/networks.json', methods=['GET'])
@login_required
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
