import os
from conflux_web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))

# Run export TESTNET_SECRET="0xxxxxxxxx" in your console, where "0xxxxxxxxx" is your testnet secret key
# You can claim testnet token at https://faucet.confluxnetwork.org/
account = web3.account.from_key(os.environ.get("TESTNET_SECRET"))
web3.wallet.add_account(account)
web3.cfx.default_account = account

balance = web3.cfx.get_balance(account.address)
assert balance > 0

# send 1 CFX to a random address
tx_hash = web3.cfx.send_transaction({
    "to": web3.account.create().address,
    "value": 1**18,
})
# in Conflux, the transaction will be executed only after it appears on the chain for 5 epoch 
# tx_hash.executed() is equivalent to web3.cfx.wait_for_transaction_receipt(tx_hash)
tx_receipt = tx_hash.executed()
print(tx_receipt)
