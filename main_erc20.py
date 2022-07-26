from hexbytes import HexBytes
from conflux_web3 import Web3 as CfxWeb3
from web3 import Web3
import json
# from conflux_module import ConfluxClient
# from typing import cast, Type
# from cfx_account import Account
from conflux_module.conflux_contract import ConfluxContract

conflux_testnet_rpc = 'https://test.confluxrpc.com'
provider = Web3.HTTPProvider(conflux_testnet_rpc)
w3 = CfxWeb3(provider=provider)
print(status := w3.cfx.get_status)
print(w3.cfx.chain_id)

private_key = "0xdcb3d3b448ff5e08ca7efeb0bdb739f6c70a680a5275e7fbea2e408c6eb1fed9"
account = w3.account.privateKeyToAccount(private_key)
addr = w3.address.encode_hex_address(account.address, w3.cfx.chain_id)
print("base32: {}".format(addr))
print("hex40: {}".format(checksumAddr := w3.address(addr).eth_checksum_address))
print(w3.cfx.get_balance(addr))

w3.cfx.default_account = addr

# tx = {
#         # 'type': "0x1",
#     'from': addr,
#     'nonce': w3.cfx.get_next_nonce(addr),
#     'gas': 21000,
#     'to': "cfxtest:aamd4myx7f3en2yu95xye7zb78gws09gj2ykmv9p58",
#     'value': 100,
#     # 'maxFeePerGas': 1000000000,
#     # 'maxPriorityFeePerGas': 1000000000,
#     'gasPrice': 10**9,
#     # 'data': b'',
#     'chainId': w3.cfx.chain_id,
#     'storageLimit': 0,
#     'epochHeight': status['epochNumber']
# }

# print(tx)

# signed = account.sign_transaction(tx)
# rawTx = signed.rawTransaction
# # print(rawTx)
# w3.cfx.send_raw_transaction(rawTx)


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
})
# tokenTx = tokenContract.functions.transfer(checksumAddr, 100).build_transaction({
#     "gas": 200000,
#     "gasPrice": 10**9,
#     'epochHeight': status['epochNumber'],
#     'storageLimit': 0,
#     'nonce': w3.cfx.get_next_nonce(addr),
# })
print(tokenTx)
# tokenTx['to'] = "cfxtest:acf3zrjx1zs4p4k2eta8je2uy4ypuzjy92dty4abt5"
signed = tx = w3.cfx.account.sign_transaction(tokenTx, private_key)
print(signed.rawTransaction)
w3.cfx.send_raw_transaction(signed.rawTransaction)

# signed = w3.eth.send_transaction(transaction)
