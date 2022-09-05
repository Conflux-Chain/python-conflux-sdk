# This example shows how to sign and send transactions without using web3.wallet
# This method provides is more flexible but is also more complex than using wallet
# If you are new to web3 development, we recommend you refer to the example to send transactions in examples/01_quick_start.py

import os, json, pprint
from conflux_web3 import Web3
from conflux_web3.utils import fill_transaction_defaults

web3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
account = web3.account.from_key(os.environ.get("TESTNET_SECRET"))

# Basiclly, we follow the workflow of 4 steps to send a transaction:
#    "build transaction" 
# -> "sign transaction" 
# -> "send transaction to the blockchain node(s)" 
# -> "wait for transaction execution result"
# if any account is added to the wallet, the first 3 steps will be combined,
# otherwise you will need to do the first 3 steps individually

# "build transaction"
# we provide necessary params here, and other params are filled
# see 11-constuct_transaction_from_scratch.py to see how to construct a transaction from scratch
built_trivial_tx = fill_transaction_defaults(web3, {
    'from': account.address,
    'to': web3.account.create().address,
    'value': 100,
})
# "sign transaction"
signed_tx = account.sign_transaction(built_trivial_tx)
# "send transaction to the blockchain node(s)"
h = web3.cfx.send_raw_transaction(signed_tx.rawTransaction)
# "wait"
tx_receipt = h.executed()
pprint.pprint(dict(tx_receipt))


# deploy a contract
# you can compile erc20 yourself 
# or use our pre-compiled file https://raw.githubusercontent.com/Conflux-Chain/python-conflux-sdk/v2/tests/_test_helpers/ERC20.json
# erc20_metadata = json.load(open("path/to/erc20metadata.json"))
erc20_metadata = json.load(open("tests/_test_helpers/ERC20.json"))
erc20 = web3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])

# "build transaction"
built_constuct_tx = erc20.constructor(name="ERC20", symbol="C", initialSupply=10**18).build_transaction({
    'from': account.address,
})
# "sign transaction"
construct_tx = account.sign_transaction(built_constuct_tx)
# "send" & "wait"
contract_address = web3.cfx.send_raw_transaction(construct_tx.rawTransaction).executed()['contractCreated']
print(f"deployed contract address: f{contract_address}")


# interact with contract
contract = web3.cfx.contract(address=contract_address, abi=erc20_metadata["abi"])
# "build transaction"
built_transfer_tx = contract.functions.transfer(
    web3.account.create().address,
    100
).build_transaction({
    'from': account.address
})
# "sign transaction"
signed_transfer_tx = account.sign_transaction(
    built_transfer_tx
)
# "send" and "wait"
print("erc20 transfer receipt: ")
pprint.pprint(
    dict(web3.cfx.send_raw_transaction(signed_transfer_tx.rawTransaction).executed())
)
