# import os
# from web3 import Web3, HTTPProvider
# # from interface import ContractInterface

# w3 = Web3(HTTPProvider('http://127.0.0.1:7545'))
# accounts = w3.eth.accounts[0]
# print(accounts)

'''
Once Ganache is installed, run its GUI or execute the following command:
$ ganache-cli -p 8545 -h 0.0.0.0 -n
'''
import json

from flask import Flask, render_template


from solc import compile_source
from web3.auto import w3

app = Flask(__name__)

contract_source_code = None
contract_source_code_file = 'contract.sol'

with open(contract_source_code_file, 'r') as file:
    contract_source_code = file.read()

contract_compiled = compile_source(contract_source_code)
contract_interface = contract_compiled['<stdin>:CoinFlip']

# Set the default account
w3.eth.defaultAccount = w3.eth.accounts[0]

# Contract abstraction
CoinFlip = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

# Create an instance, i.e., deploy on the blockchain
tx_hash = CoinFlip.constructor().transact({'from':w3.eth.accounts[0]})
# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# Contract Object
coinflip = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])


# print('Calling contract functions')
# print('Contract address: ', coinflip.address)
# print(example.functions.fibonacciB(10).transact())
# print(example.functions.fibonacciA(10).transact({'from':w3.eth.accounts[0],'value': w3.toWei(1,'ether')}))

# print(ans)

# Web service initialization
@app.route('/')
@app.route('/index')
def hello():
    return render_template('coinflip.html', contractAddress = coinflip.address.lower(), contractABI = json.dumps(contract_interface['abi']))

@app.route('/bettor')
def bettor():
    return render_template('coinflip.html', contractAddress = coinflip.address.lower(), contractABI = json.dumps(contract_interface['abi']))


@app.route('/bettee')
def bettee():
    return render_template('coinflip_bettee.html', contractAddress = coinflip.address.lower(), contractABI = json.dumps(contract_interface['abi']))


if __name__ == '__main__':
    app.run()
