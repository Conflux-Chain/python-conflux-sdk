# ## conflux-web3 code example 01: quickstart
# 
# Run this example online --> [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Conflux-Chain/python-conflux-sdk/dev?labpath=examples%2Fipynb%2F01-quick_start.ipynb)
# 
# This example will present:
# 
# * how to connect to the blockchain via a node
# * how to create and use an account
# * how to interact with a contract or simply send a transaction

# ### Connect to a Node
# 
# We are supposed to connect to the Conflux network via a node. You can run a node locally following [this tutorial](https://developer.confluxnetwork.org/conflux-doc/docs/get_started/) but the node might occupy lots of resources. In this example, we connect to the [Conflux testnet public RPC endpoint](https://developer.confluxnetwork.org/sdks-and-tools/en/conflux_rpcs).

from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
assert w3.is_connected()

# ### Create an Account
# 
# In web3, typically, owning an account means knowing a **secret**, or **private key**. This secret should be kept secret and no one else knows it.
# 
# Now we will create a new account by using `w3.account.create()`. This function generates an account from a random secret key. And as this account is generated from a random key, its balance is supposed to be `0`.
# 
# It is also supported to use `w3.account.from_key("0x....")` to use your secret key (**but don't run it in an unsafe environment!**)

acct = w3.account.create()
print(f"account address: {acct.address}")
# WARNING: Don't run the following line in production environment, private key should be kept secret
print(f"account secret key: {acct._private_key.hex()}")
balance = w3.cfx.get_balance(acct.address)
assert balance == 0
print(f"balance for {acct.address}: {balance}")

# ### Claim CFX via Testnet Faucet Contract
# 
# Because the account's balance is `0`, it cannot afford the **gas** required to send a transaction. However, Conflux's [sponsorship mechanism](https://forum.conflux.fun/t/conflux-sponsorship-mechanism/12764) allows user to interact with a smart contract without paying gas, so we can claim CFX from [testnet faucet](https://testnet.confluxscan.net/address/cfxtest:acejjfa80vj06j2jgtz9pngkv423fhkuxj786kjr61).
# 
# > What is a smart contract? A smart contract is a program deployed on the blockchain network. It provides interfaces to complete specific logic. In the example, invoking the `claimCfx` method of faucet contract will give you 1000 testnet CFX.

# Firstly we will set `w3.cfx.default_account` to `acct``, after that transactions can be automatically sent.
w3.cfx.default_account = acct

# Next we will interact with testnet Faucet contract
faucet = w3.cfx.contract(name="Faucet")
tx_hash = faucet.functions.claimCfx().transact()

print(f"tx hash is: {tx_hash.hex()}\n"
      f"conflux scan link: https://testnet.confluxscan.net/transaction/{tx_hash.hex()}")

# in Conflux, the transaction will be executed only after it appears on the chain for 5 epoch
# `tx_hash.executed()` is equivalent to `w3.cfx.wait_for_transaction_receipt(tx_hash)`
tx_hash.executed()
print(f"balance for {acct.address}: {w3.cfx.get_balance(acct.address).to('CFX')}")

# ### Send CFX to Others
# 
# Now we have plenty of testnet CFX to do whatever you want. For example, we can send 1 CFX to zero address.

# Now acct has CFX
# send 1 CFX to zero address
w3.cfx.send_transaction({
    "to": w3.address.zero_address(),
    "value": 10**18,
}).executed()
print(f"balance for {acct.address}: {w3.cfx.get_balance(acct.address).to('CFX')}")

