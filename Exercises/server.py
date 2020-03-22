from flask import Flask, request, render_template, redirect, request, url_for
from blockchain import *
import requests
import base64


# Initialize flask application
app =  Flask(__name__)

# Initialize public and private key
private_key = SigningKey.generate(curve=NIST384p)
public_key = private_key.verifying_key
base64encoded_public_key = base64.encodestring(public_key.to_string())

# Initialize a blockchain object.
blockchain = Blockchain()

# Initialize a Miner object.
miner = Miner(public_key)

# public keys of other participating members of the network
all_public_keys = set()
all_public_keys.add(base64encoded_public_key)

# the address to other participating members of the network
peers = set()
peers.add(u"http://127.0.0.1:8000/")

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []

@app.route('/')
def index():
    print(blockchain.forked_chains)
    print(blockchain.chain)
    return render_template('index.html',
                           title='SUTD COIN '
                                 'Decentralised Transaction Ledger',
                           peers = peers,
                           encoded_public_key = base64encoded_public_key,
                           public_keys = all_public_keys,
                           posts=posts,
                           forked = blockchain.forked,
                           current_length = len(blockchain.chain),
                           coins=blockchain.coins.get(str(public_key)),
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

@app.route('/get_headers')
def get_headers():
    headers = {}
    for block in blockchain.chain:
        headers[block.index] = block.header
    print(json.dumps(headers))
    return json.dumps(headers)

@app.route('/get_coins', methods=['POST'])
def get_coins():
    client = request.get_json()["client"]
    print(client)
    print(blockchain.coins)
    if (blockchain.coins.get(client) == None):
        blockchain.coins[client] = 0
    result = {"coins": blockchain.coins[client]}
    return json.dumps(result)
    

@app.route('/get_public_keys')
def get_public_keys():
    response = requests.get(CONNECTED_NODE_ADDRESS + "/return_public_keys")
    retrieved_public_keys = response.json()["public_keys"]
    all_public_keys.update(retrieved_public_keys)
    return redirect(url_for('index'))

# endpoint to return public_keys from main node
@app.route('/return_public_keys')
def return_public_keys():
    return json.dumps({"public_keys": list(all_public_keys)})

# endpoint to submit a new transaction. This will be used by
# our application to add new data (transactions) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
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

        blockchain.add_new_transaction(mk)

        return "Success", 201

    except Exception as e:
            return(str(e), 400)

@app.route('/spv_new_transaction', methods=['POST'])
def spv_new_transaction():
    data = request.get_json()["root"]["data"]

    sender = data["sender"]
    receiver = data["receiver"]
    amount = data["amount"]
    comment = data["comment"]
    tx = Transaction(sender, receiver, amount, comment)

    mk = MerkleTree([tx])
    blockchain.unconfirmed_transactions.append(mk)

    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    json_chain = json.dumps(blockchain.__dict__, cls=ComplexEncoder)
    decoded_json = json.loads(json_chain)
    decoded_json["peers"] = list(peers)
    decoded_json["length"] = len(blockchain.chain)
    final_json = json.dumps(decoded_json, sort_keys=True)
    print(final_json)
    return final_json
    # for block in blockchain.chain:
    #     chain_data.append(block.__dict__)
    # return json.dumps({"length": len(chain_data),
    #                    "chain": chain_data,
    #                    "coins": blockchain.coins,
    #                    "locked_coins": blockchain.locked_coins,
    #                    "peers": list(peers)})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['POST'])
def mine_unconfirmed_transactions():
    mining_params = request.form
    target_fork = mining_params["target_fork"]
    new_fork = mining_params["new_fork"]
    if (mining_params["index"] == ""):
        index = None
    else:
        index = int(mining_params["index"])
    
    if str(target_fork) == "":
        result = miner.mine(blockchain)
    else:
        result = miner.mine(blockchain, target_fork, new_fork, index)
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        blockchain.forked = False
        result = blockchain.resolve()
        if result == True:
            blockchain.forked = True
        if result == False:
            return "Block #{} is mined.".format(blockchain.forked_chains[new_fork][-1].index)
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    new_public_key = request.get_json()["public_key"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)
    # Add public key to all public keys list
    all_public_keys.add(new_public_key)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url, "public_key": base64.encodestring(public_key.to_string())}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        coins = response.json()['coins']
        locked_coins = response.json()['locked_coins']
        blockchain = create_chain_from_dump(chain_dump)
        blockchain.coins = coins
        blockchain.locked_coins = locked_coins
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code

# endpoint to add new spv_clients to the network.
@app.route('/register_spv', methods=['POST'])
def register_spv():
    node_address = request.get_json()["node_address"]
    new_public_key = request.get_json()["public_key"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)
    # Add public key to all public keys list
    all_public_keys.add(new_public_key)

    # Return all headers to the newly registered spv client
    # so that he can sync
    return get_headers()


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        added = generated_blockchain.quick_add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    data = request.get_json()
    coins = data["coins"]
    locked_coins = data["locked_coins"]
    block = Block(data["index"],
                  data["transactions"],
                  str(data["header"]["previous_hash"]),
                  str(data["header"]["hash_merkle_root"]),
                  data["header"]["timestamp"],
                  data["header"]["nonce"],
                  )

    proof = data['hash']
    added = blockchain.quick_add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    blockchain.coins = coins
    blockchain.locked_coins = locked_coins

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        if response.status_code != 200:
            continue
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        json_data = json.dumps(block.reprJSON(), cls=ComplexEncoder)
        decoded_json = json.loads(json_data)
        decoded_json["coins"] = blockchain.coins
        decoded_json["locked_coins"] = blockchain.locked_coins
        encoded_json = json.dumps(decoded_json, sort_keys=True)

        requests.post(url,
                      data= encoded_json,
                      headers=headers)

# Uncomment this line if you want to specify the port number in the code
#app.run(debug=True, port=8000)
