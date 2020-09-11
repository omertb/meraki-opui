import json, requests, os


APIKEY = os.environ['APIKEY']
BASE_URL = 'https://api.meraki.com/api/v1/'
BASE_URLv0 = 'https://api.meraki.com/api/v0/'

cred_header = {
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'X-Cisco-Meraki-API-Key': APIKEY
}


def get_datav0(uri) -> list:
    url = "{}{}".format(BASE_URLv0, uri)
    response = requests.request("GET", url, headers=cred_header)
    if response.status_code == 200:
        response_list = json.loads(response.text)
        return response_list
    else:
        print("Meraki Server Response: {} | Code: {}".format(response, response.status_code))
        raise requests.exceptions.ConnectionError


def get_data(uri) -> list:
    url = "{}{}".format(BASE_URL, uri)
    response = requests.request("GET", url, headers=cred_header)
    if response.status_code == 200:
        response_list = json.loads(response.text)
        return response_list
    elif response.status_code == 404:
        return response.status_code
    else:
        print("Meraki Server Response: {} | Code: {}".format(response, response.status_code))
        raise requests.exceptions.ConnectionError


def post_data(uri, data_dict, method="POST", base_url=BASE_URL) -> list:
    url = "{}{}".format(base_url, uri)
    data = json.dumps(data_dict)
    response = requests.request(method, url, headers=cred_header, data=data)
    if response.status_code == 200:
        if response.text.strip():
            response_list = json.loads(response.text)
            return response_list
        else:
            return "success"
    elif response.status_code == 201:
        print("created")
        response_dict = json.loads(response.text)
        return response_dict
    elif response.status_code == 204:
        print("deleted")
        return "success"
    elif response.status_code == 400:
        return json.loads(response.text)
    elif response.status_code == 401:
        return json.loads(response.text)
    else:
        print("Meraki Server Response: {} | Code: {}".format(response.text, response.status_code))
        raise requests.exceptions.ConnectionError


#  READ FUNCTIONS

def get_organization_ids() -> list:
    org_data_list = get_data("organizations")
    org_id_list = []
    for organization in org_data_list:
        org_id_list.append(organization['id'])
    return org_id_list


def get_templates() -> dict:
    org_id_list = get_organization_ids()
    templates_dict = {}
    for org_id in org_id_list:
        templates = get_data('organizations/{}/configTemplates'.format(org_id))
        templates_dict.update({i['name']: i['id'] for i in templates})
    return templates_dict


def get_networks() -> list:
    org_id_list = get_organization_ids()
    networks_list = []
    for org_id in org_id_list:
        networks = get_datav0('organizations/{}/networks'.format(org_id))
        networks_list.extend(networks)

    # create customized dictionary list
    networks_dict_list = []
    for network in networks_list:
        dict_item = {'net_name': network['name'],
                     'net_type': " ".join(network['productTypes']),
                     'meraki_id': network['id'],
                     'net_tags': network['tags'].strip() if network['tags'] else None,
                     'bound_template': network['configTemplateId'] if 'configTemplateId' in network else None
                     }
        networks_dict_list.append(dict_item)

    return networks_dict_list


def get_devices() -> list:
    org_id_list = get_organization_ids()
    dev_status_list = []
    for org_id in org_id_list:
        dev_status = get_datav0('organizations/{}/deviceStatuses'.format(org_id))
        dev_status_list.extend(dev_status)
    return dev_status_list


def get_device(serial):
    uri = "devices/{}".format(serial)
    response = get_data(uri)
    return response


def get_network(network_id):
    uri = "networks/{}".format(network_id)
    response = get_data(uri)
    return response

#  WRITE FUNCTIONS

def create_network(network_dict: dict):
    org_id = get_organization_ids()[0]
    uri = "organizations/{}/networks".format(org_id)
    response = post_data(uri, network_dict)
    return response


def bind_template(network_id: str, template_id: str):
    uri = "networks/{}/bind".format(network_id)
    post_data_dict = {}
    post_data_dict['configTemplateId'] = template_id
    response = post_data(uri, post_data_dict)
    return response


def claim_network_devices(network_id: str, serials_list: list):
    uri = "networks/{}/devices/claim".format(network_id)
    post_data_dict = {}
    post_data_dict['serials'] = serials_list
    response = post_data(uri, post_data_dict)
    return response


def rename_device(serial: str, name: str):
    uri ="devices/{}".format(serial)
    serial_dict = {}
    serial_dict['serial'] = serial
    serial_dict['name'] = name
    response = post_data(uri, serial_dict, method="PUT")
    return response


def rename_device_v0(network_id: str, serial: str, name: str):
    uri ="networks/{}/devices/{}".format(network_id, serial)
    serial_dict = {}
    serial_dict['serial'] = serial
    serial_dict['name'] = name
    response = post_data(uri, serial_dict, method="PUT", base_url=BASE_URLv0)
    return response


# DELETE FUNCTIONS

def remove_network_device(network_id: str, serial: str):
    uri = "/networks/{}/devices/remove".format(network_id)
    serial_dict = {}
    serial_dict['serial'] = serial
    response = post_data(uri, serial_dict)
    return response


def delete_network(network_id: str):
    uri = "/networks/{}".format(network_id)
    response = post_data(uri, "", method="DELETE")
    return response
