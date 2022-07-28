from hexbytes import HexBytes
from conflux_web3 import Web3 as CfxWeb3
from web3 import Web3
import json
from conflux_module.contract import ConfluxContract

conflux_testnet_rpc = 'https://test.confluxrpc.com'
provider = Web3.HTTPProvider(conflux_testnet_rpc)
w3 = CfxWeb3(provider=provider)
print(status := w3.cfx.get_status)
print(w3.cfx.chain_id)

private_key = "0xxxxxxx"
account = w3.account.privateKeyToAccount(private_key)
addr = w3.address.encode_hex_address(account.address, w3.cfx.chain_id)
print("base32: {}".format(addr))
print("hex40: {}".format(checksumAddr := w3.address(addr).eth_checksum_address))
print(w3.cfx.get_balance(addr))

w3.cfx.default_account = addr

erc20 = json.load(open("conflux_module/contracts/ERC20.json"))
abi = erc20["abi"]

tokenContract = w3.cfx.contract(address="cfxtest:acf3zrjx1zs4p4k2eta8je2uy4ypuzjy92dty4abt5", abi=abi)
# signed = tx = w3.eth.account.sign_transaction(transaction, private_key)
# print(signed.rawTransaction)
tokenTx = tokenContract.functions.transfer(addr, 100).build_transaction({
    "gas": 200000,
    "gasPrice": 10**9,
    'epochHeight': status['epochNumber'],
    'storageLimit': 0,
    'nonce': w3.cfx.get_next_nonce(addr),
    'chainId': w3.cfx.chain_id,
})

print(tokenTx)
# tokenTx['to'] = "cfxtest:acf3zrjx1zs4p4k2eta8je2uy4ypuzjy92dty4abt5"
signed = tx = w3.cfx.account.sign_transaction(tokenTx, private_key)
print(signed.rawTransaction)
w3.cfx.send_raw_transaction(signed.rawTransaction)

# signed = w3.eth.send_transaction(transaction)


from web3 import Web3, EthereumTesterProvider
# w3 = Web3(Web3.HTTPProvider('https://evmtestnet.confluxrpc.com'))
w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/913367d4b3344b35a6de1ff9127e7376'))
print(w3.isConnected())

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware.signing import construct_sign_and_send_raw_middleware
import json

ethprivate_key = "0xxxxxxx"
ethaccount: LocalAccount = Account.from_key(ethprivate_key)
print(ethaccount.address)
print(w3.eth.get_balance(ethaccount.address))

w3.middleware_onion.add(construct_sign_and_send_raw_middleware(ethaccount))
w3.eth.default_account = ethaccount.address

# from eth_account.messages import encode_defunct

# msg = encode_defunct(text="Conflux")
# w3.eth.account.sign_transaction(msg, private_key=private_key)

# transaction = {
#     # 'type': '0x1',
#     # 'from': account.address,
#     'nonce': w3.eth.get_transaction_count(account.address),
#     'gas': 21000,
#     'to': "0xd43d2a93e97245E290feE74276a1EF8D275bE646",
#     'value': 100,
#     'maxFeePerGas': 1000000000,
#     'maxPriorityFeePerGas': 1000000000,
#     # 'gasPrice': 10**9,
#     # 'data': b'',
#     'chainId': w3.eth.chain_id
# }

# rawTx = w3.eth.account.sign_transaction(transaction, private_key).rawTransaction

# w3.eth.send_raw_transaction(rawTx)

# # w3.eth.send_transaction(transaction)

# erc20 = json.load(open("py/ERC20.json"))

# abi = erc20["abi"]

ethTokenContract = w3.eth.contract(address="0x0E88fA4C0feA89bb5Fd992e3d060fd54dbe4f8A0", abi=abi)
# signed = tx = w3.eth.account.sign_transaction(transaction, private_key)
# print(signed.rawTransaction)
ethContractTx = ethTokenContract.functions.transfer("0xd43d2a93e97245E290feE74276a1EF8D275bE646", 1)
ethContractTx.transact({
    "gasPrice": 10**9,
})
# w3.eth.send_raw_transaction(signed.rawTransaction)

# signed = w3.eth.send_transaction(transaction)


