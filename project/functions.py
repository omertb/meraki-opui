import json, requests, os

APIKEY = os.environ['APIKEY']
BASE_URL = 'https://api.meraki.com/api/v1/'

cred_header = {
    'X-Cisco-Meraki-API-Key': APIKEY
}


def get_data(item) -> list:
    url = "{}{}".format(BASE_URL, item)
    response = requests.request("GET", url, headers=cred_header)
    if response.status_code == 200:
        response_list = json.loads(response.text)
        return response_list
    else:
        print("Meraki Server Response: {} | Code: {}".format(response, response.status_code))
        raise requests.exceptions.ConnectionError


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
        networks = get_data('organizations/{}/networks'.format(org_id))
        networks_list.extend(networks)

    # create customized dictionary list
    networks_dict_list = []
    for network in networks_list:
        dict_item = {'net_name': network['name'],
                     'net_type': " ".join(network['productTypes']),
                     'meraki_id': network['id'],
                     'net_tags': network['tags'] if network['tags'] else None,
                     'bound_template': network['configTemplateId'] if 'configTemplateId' in network else None
                     }
        networks_dict_list.append(dict_item)

    return networks_dict_list


def get_devices() -> list:
    org_id_list = get_organization_ids()
    dev_status_list = []
    for org_id in org_id_list:
        dev_status = get_data('organizations/{}/devices/statuses'.format(org_id))
        dev_status_list.extend(dev_status)
    return dev_status_list