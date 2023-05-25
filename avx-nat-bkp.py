'''
Script to backup all DNAT rules from all Aviatrix gateways.
Remember that this is a script adapted for a specific need, with some exceptions such as removing gateways that contain "firenet" or "ingress" as part of the name. Feel free to copy and adapt the script as needed.
'''
import json
import os
import sys
import requests

controller_cid = None
controller_url = "avx-controller.testdevs.com.br"
controller_username = os.environ["AVX_USERNAME"]
controller_password = os.environ["AVX_PASSWORD"]
file_path = "./gateways.yaml"

def aviatrix_login():
    payload = {
        "action": "login",
        "username": controller_username,
        "password": controller_password
    }
    request = requests.post(f'https://{controller_url}/v1/api', data=payload)
    if request.status_code != 200:
        print("Unable to login to Aviatrix!")
        return False
    response = request.json()
    cid = response["CID"]
    return cid

def aviatrix_get_nats(CID, gateway_name):
    request = requests.get(
        f'https://{controller_url}/v1/api?action=get_gateway_dnat_config&CID={CID}&gateway_name={gateway_name}')
    result = request.json()
    nats = json.loads(result["results"])
    return nats

def aviatrix_get_all_gateway_names(CID):
    request = requests.get(
        f'https://{controller_url}/v1/api?action=list_vpcs_summary&CID={CID}')
    result = request.json()
    remove_firenet = [gateway for gateway in result["results"] if "firenet" not in gateway["gw_name"] and "ingress" not in gateway["gw_name"]]
    gateway_names = [gateway["gw_name"] for gateway in remove_firenet]
    return gateway_names

def backup_nat_rules(CID, gateway_names):
    for gateway_name in gateway_names:
        nats = aviatrix_get_nats(CID, gateway_name)
        #Save DNAT rules to files
        base_path = os.path.join(os.getcwd(), "..", "..", "current-avx-nat-rules")
        file_name = f"{gateway_name}_nat_rules.json"
        file_path = os.path.join(base_path, file_name)
        with open(file_path, "w") as file:
            json.dump(nats, file, indent=4)
        print(f"Backup das regras de NAT para {gateway_name} concluído.")




cid = aviatrix_login()
if not cid:
    print("Unable to login to Aviatrix!")
    sys.exit()

all_gateway_names = aviatrix_get_all_gateway_names(cid)
backup_nat_rules(cid, all_gateway_names)


