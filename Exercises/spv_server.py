from flask import Flask, request, render_template, redirect, request, url_for
from blockchain import *
from spvclient import *
import requests
import base64


# Initialize flask application
app =  Flask(__name__)

# Initialize public and private key
private_key = SigningKey.generate(curve=NIST384p)
public_key = private_key.verifying_key
base64encoded_public_key = base64.encodestring(public_key.to_string())

client = SPVClient([], private_key, public_key)

# public keys of other participating members of the network
all_public_keys = set()
all_public_keys.add(base64encoded_public_key)

# the address to other participating members of the network
peers = set()
peers.add(u"http://127.0.0.1:8000/")


# The node with which the spv client interacts with, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"



@app.route('/')
def index():
    print(client.blockheaders)
    return render_template('spv_index.html',
                           title='SUTD COIN '
                                 'Decentralised Transaction Ledger',
                           peers = peers,
                           encoded_public_key = base64encoded_public_key,
                           public_keys = all_public_keys,
                           coins=100,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

@app.route('/get_headers')
def get_headers():


    response = requests.get(CONNECTED_NODE_ADDRESS + "/get_headers")

    if response.status_code == 200:
        client.blockheaders = []
        headers = response.json()
        for value in headers.values():
          client.add_new_header(value)
        return "Registration successful and retrieved all headers", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code

@app.route('/spv_register_with', methods=['POST'])
def spv_register_with_existing_node():

    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url, "public_key": base64.encodestring(public_key.to_string())}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_spv",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        headers = response.json()
        for value in headers.values():
          client.add_new_header(value)
        return "Registration successful and retrieved all headers", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code
