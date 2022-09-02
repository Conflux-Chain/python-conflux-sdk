import os
from cfx_address import Base32Address
from conflux_web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
# web3.account is a cfx_account.Account object inherited from eth_account.Account
# most of its apis are consistent with eth_account (https://eth-account.readthedocs.io/en/stable/eth_account.html)
random_account = web3.account.create()
# account created from web3.account will have the same network_id as web3.cfx.chain_id
print(f"network id of the account: {random_account.network_id}")

# a Base32Address object, see https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-37.md for more information
addr = random_account.address

print(f"account address: {addr}") # expected to be cfxtest:a....
print(f"account private key: {addr}")

# the network id of an account can be set
random_account.network_id = 1029
print(f"account address after network id changing: {random_account.address}") # expected to be cfx:a....



# a Base32Address is also a str
assert isinstance(addr, Base32Address)
assert isinstance(addr, str)
# visit https://conflux-fans.github.io/cfx-address/cfx_address.html#module-cfx_address.address for more information
address = Base32Address("0x1ecde7223747601823f7535d7968ba98b4881e09", network_id=1)
print([
    address.address_type,
    address.network_id,
    address.hex_address,
    address.verbose_address,
    address.abbr,
    address.mapped_evm_space_address,
    address.eth_checksum_address,
])



# wallet serves as a middleware for conflux_web3 and contains a collection of LocalAccount
assert web3.wallet is web3.middleware_onion["wallet"]
secret = os.environ.get("TESTNET_SECRET")
account = web3.account.from_key(secret)

random_account.network_id = web3.cfx.chain_id
web3.wallet.add_account(account)
# if the transaction["from"] account is in the wallet
web3.cfx.send_transaction({
    "from": account.address,
    "to": random_account.address,
    "value": 10**18
}).executed()

# or set the web3.cfx.default_account, then the from field of the transaction can be automatically filled
web3.cfx.default_account = account.address
web3.cfx.send_transaction({
    "to": random_account.address,
    "value": 10**18
}).executed()
