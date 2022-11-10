# ## `conflux-web3` Code Example 10: Send a Transaction without Wallet
# 
# This example shows how to sign and send transactions without using `w3.wallet`. This method is more flexible but simultaneously more complex to use. If you are new to web3 development, we recommend you refer to the example to send transactions in [quickstart](./01-quickstart.ipynb)

import pprint
from conflux_web3 import Web3
from conflux_web3.utils import fill_transaction_defaults

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
account = w3.account.from_key("0x....") # fill your secret key here

# ## Manully Send a Transaction
# 
# Basiclly, we follow the workflow of 4 steps to send a transaction:
# 
# * build transaction
# * sign transaction
# * send transaction to the blockchain node(s)
# * wait for transaction execution result
# 
# If any account is added to the `w3.wallet`, the first 3 steps will be combined,
# otherwise you will need to do the first 3 steps manully

# ### Build a Simple Transaction
# Only necessary parameters are provided here, and other params are filled by `fill_transaction_defaults`.
# Refer to [constuct_transaction_from_scratch](./11-constuct_transaction_from_scratch.ipynb) to see how to construct a transaction from scratch.

built_trivial_tx = fill_transaction_defaults(w3, {
    'from': account.address,
    'to': w3.account.create().address,
    'value': 100,
})

# ### Sign a Transaction

signed_tx = account.sign_transaction(built_trivial_tx)

# ### Send Transaction

h = w3.cfx.send_raw_transaction(signed_tx.rawTransaction)

# ### Wait

tx_receipt = h.executed()

# ## Interact with Contract without Wallet

# if you want to get contract object from metadata file, use
# >>> erc20_metadata = json.load(open("path/to/ERC20metadata.json"))
# >>> erc20 = web3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
erc20 = w3.cfx.contract(name="ERC20")

# "build transaction"
built_constuct_tx = erc20.constructor(name="Coin", symbol="C", initialSupply=10**18).build_transaction({
    'from': account.address,
})
# "sign transaction"
construct_tx = account.sign_transaction(built_constuct_tx)
# "send" & "wait"
contract_address = w3.cfx.send_raw_transaction(construct_tx.rawTransaction).executed()['contractCreated']
print(f"deployed contract address: {contract_address}")

# interact with the deployed contract
contract = w3.cfx.contract(address=contract_address, name="ERC20")
# "build transaction"
built_transfer_tx = contract.functions.transfer(
    w3.account.create().address,
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
    dict(w3.cfx.send_raw_transaction(signed_transfer_tx.rawTransaction).executed())
)

