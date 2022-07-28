from hexbytes import HexBytes
from conflux_web3 import Web3 as CfxWeb3
from web3 import Web3
import json

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
