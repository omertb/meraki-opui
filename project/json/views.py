from project import db
from project.models import Network, Device
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user


# home blueprint definition
json_blueprint = Blueprint('json', __name__, template_folder='templates')


@json_blueprint.route('/delete_networks', methods=['POST'])
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


@json_blueprint.route('/network.json', methods=['GET'])
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
                device_list.append(device)
                i += 1
        return jsonify(device_list)
    else:
        return "Not Found", 404
