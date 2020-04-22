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
contract_source_code_file = 'fibonacci.sol'

with open(contract_source_code_file, 'r') as file:
    contract_source_code = file.read()

# Compile the contract
contract_compiled = compile_source(contract_source_code)
contract_interface = contract_compiled['<stdin>:Fib']

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


print('Calling contract functions')
print('Contract address: ', example.address)
print('obj.getOwner(): ', example.functions.getOwner().call())
print(example.functions.newFibonacciB(10).transact())
# print(example.functions.fibonacciB(10).transact())
# print(example.functions.fibonacciA(10).transact({'from':w3.eth.accounts[0],'value': w3.toWei(1,'ether')}))

# print(ans)
