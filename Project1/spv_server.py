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
# Default connected_node_addr
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"



@app.route('/')
def index():
    print("blockheaders:")
    print(client.blockheaders)
    get_coins()
    return render_template('spv_index.html',
                           title='SUTD COIN '
                                 'Decentralised Transaction Ledger',
                           peers = peers,
                           encoded_public_key = base64encoded_public_key,
                           blockheaders = client.blockheaders,
                           public_keys = all_public_keys,
                           coins=client.coins,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

def get_coins():
    try:
        data = {"client": str(public_key)}
        headers = {'Content-Type': "application/json"}
        response = requests.post(CONNECTED_NODE_ADDRESS + "/get_coins",
                             data=json.dumps(data), headers=headers)

        coins = response.json()["coins"]
        client.coins = int(coins)

        return "Transaction Sent", 200

    except Exception as e:
        return(str(e), 400)

# endpoint that calls connected node to get all public keys
@app.route('/get_public_keys')
def get_public_keys():
    response = requests.get(CONNECTED_NODE_ADDRESS + "/return_public_keys")
    retrieved_public_keys = response.json()["public_keys"]
    all_public_keys.update(retrieved_public_keys)
    return redirect(url_for('index'))

# endpoint that calls connected node to get all headers
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

# endpoint that sends transaction to connected node
@app.route('/send_transaction', methods=['POST'])
def send_transaction():

    try:
        tx_data = request.form
        required_fields = ["receiver", "amount", "comment"]

        for field in required_fields:
            if not tx_data.get(field):
                return "Invalid transaction data", 404
        
        encoded_sender_key = base64.encodestring(public_key.to_string())
        tx = Transaction(encoded_sender_key, tx_data["receiver"], int(tx_data["amount"]), tx_data["comment"])
        tx.sign(private_key)
        mk = MerkleTree([tx])
        headers = {'Content-Type': "application/json"}
        response = requests.post(CONNECTED_NODE_ADDRESS + "/spv_new_transaction",
                             data=json.dumps(mk.__dict__, cls=ComplexEncoder), headers=headers)

        return "Transaction Sent", 200

    except Exception as e:
        return(str(e), 400)

# endpoint registers spv client with specified node
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
