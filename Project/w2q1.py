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

from solc import compile_source
from web3.auto import w3


contract_source_code = None
contract_source_code_file = 'example.sol'

with open(contract_source_code_file, 'r') as file:
    contract_source_code = file.read()

# Compile the contract
contract_compiled = compile_source(contract_source_code)
contract_interface = contract_compiled['<stdin>:Example']

# Set the default account
w3.eth.defaultAccount = w3.eth.accounts[0]

# Contract abstraction
Example = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

# Create an instance, i.e., deploy on the blockchain
tx_hash = Example.constructor().transact()
# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# Contract Object
example = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])

#Sending transactions from acconut 1 to acccount 2
signed_txn = w3.eth.account.signTransaction(dict(
    nonce=w3.eth.getTransactionCount(w3.eth.accounts[0]),
    gasPrice = w3.eth.gasPrice, 
    gas = 100000,
    to=w3.eth.accounts[1],
    value=w3.toWei(10,'ether')
  ),
  '41d8bd50fe42d09b87b36d146f299cad2a7db26ec6be61382d28ee748fff7299')

tx_sent = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
tx_receipt_1 = w3.eth.waitForTransactionReceipt(tx_sent)
print(tx_receipt_1)

print('Calling contract functions')
print('Contract address: ', example.address)
print('obj.getOwner(): ', example.functions.getOwner().call())


