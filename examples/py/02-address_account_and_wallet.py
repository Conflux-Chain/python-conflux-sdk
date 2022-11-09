# ## conflux-web3 code example 02: account, address and wallet
# 
# Run this example online --> [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Conflux-Chain/python-conflux-sdk/dev?labpath=examples%2Fipynb%2F02-address_account_and_wallet.ipynb)

# ### Preparation
# 
# This is the preparation part, we prepare the `web3` instance and `private_key`.

# prerequisites: 
# we create an account and claim 1000 CFX from the faucet
from pprint import pprint
from conflux_web3 import Web3

w3_ = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))

acct = w3_.account.create()

w3_.cfx.default_account = acct

faucet = w3_.cfx.contract(name="Faucet")
tx_receipt = faucet.functions.claimCfx().transact().executed()

# we use a new w3 object for the following presentation
w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
private_key: str = acct._private_key.hex()

# ### Account and Address
# 
# In web3, typically, owning an account means knowing a **secret**, or **private key**. This secret should be kept secret and no one else knows it.
# 
# Although private should be kept secret, ***address*** can be revealed. Address is a string derived from the private key, and identifies an account. In Conflux, addresses are encoded in base32 format.


# #### `LocalAccount` Object
# 
# `w3.account` is a factory which is used to produce `LocalAccount` objects (e.g. `random_account`). `LocalAccount` object contains the account secret and can be used to sign transactions.
# 
# **NOTE: It is not recommended to manually sign the tx because it is tedious, refer to [wallet](#wallet) part to see how to sign and send a transaction by using wallet. Or you can refer to [construct_transaction_from_scratch](./11-construct_transaction_from_scratch.ipynb) to see how to manually sign transactions correctly.**
# 
# > More documents: `w3.account` is a `cfx_account.Account` object inherited from `eth_account.Account`, and most of its apis are consistent with [eth_account](https://eth-account.readthedocs.io/en/stable/eth_account.html).

random_account = w3.account.from_key(private_key)
print(f"account address: {random_account.address}")
print(f"account private key: {private_key}")

transaction = {
    'to': w3.address.zero_address(),
    'nonce': 1,
    'value': 1,
    'gas': 21000,
    'gasPrice': 10**9,
    'storageLimit': 0,
    'epochHeight': 100,
    'chainId': 1
}
print(f"signed raw tx: {random_account.sign_transaction(transaction).rawTransaction.hex()}")

# #### Conflux Addresses
# 
# In Conflux, addresses are encoded in base32 format following [CIP-37](https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-37.md). You can infer which network the address belongs to simply from the address literal.

# "cfxtest" marks an address in testnet
assert random_account.address.startswith("cfxtest:")

# The addresses returned by SDK are all wrapped by class `Base32Address`. The class provides convenient methods to operate base32 addresses, but you can also use `Base32Address` object as trivial python `str` object. 
# You can visit [Base32Address documentation](https://conflux-fans.github.io/cfx-address/cfx_address.html#module-cfx_address.address) for more information.

addr = random_account.address
print(f"the type of addr: {type(addr)}")
# a Base32Address object is also a `str`
assert isinstance(addr, str)

# encode a base32 address from hex address and network_id
# it is also supported to use `w3.address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")`
address = w3.address("0x1ecde7223747601823f7535d7968ba98b4881e09", network_id=1)
print(address)
pprint([
    address.address_type,
    address.network_id,
    address.hex_address,
    address.verbose_address,
    address.abbr,
    address.mapped_evm_space_address,
    address.eth_checksum_address,
])

# ### Wallet
# 
# We use a `wallet` middleware to help us sign transactions. `w3.wallet` will sign the unsigned transaction sent via `w3.cfx.send_transaction` if it has the account of `from` address.
# 
# > `wallet` middleware follows the implementation of `web3.py`'s `construct_sign_and_send_middleware`, but provides more feature. For example, we can use `w3.wallet.add_account`, `w3.wallet.add_accounts`, `w3.wallet.pop` to add or remove accounts dynamically. 

# wallet serves as a middleware for conflux_web3 and contains a collection of LocalAccount
assert w3.wallet is w3.middleware_onion["wallet"]

w3.wallet.add_account(random_account)

assert random_account.address in w3.wallet
w3.cfx.send_transaction({
    "from": random_account.address,
    "to": random_account.address,
    "value": 10**18
}).executed()

# #### Syntactic Sugar of `w3.cfx.default_account`
# 
# If `w3.cfx.default_account` is set, a transaction without `from` field will be considered from `w3.cfx.default_account`. 
# 
# `w3.cfx.default_account` is an address, but you can set it using a `LocalAccount` object. In this case, the provided account will be added to the wallet at the same time. 
# 
# ```python
# w3.cfx.default_account = random_account
# ```
# 
# is equivalent to
# 
# ```python
# w3.cfx.default_account = random_account.address
# w3.wallet.add_account(random_account)
# ```

