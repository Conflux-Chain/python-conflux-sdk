from pathlib import Path
import sys
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))
print(sys.path)

from conflux_web3 import Web3 as CfxWeb3
from web3 import Web3
# from conflux_module import ConfluxClient
# from typing import cast, Type
# from cfx_account import Account

conflux_testnet_rpc = 'https://test.confluxrpc.com'
provider = Web3.HTTPProvider(conflux_testnet_rpc)
w3 = CfxWeb3(provider=provider)
print(status := w3.cfx.get_status)
print(w3.cfx.chain_id)

private_key = "0xxxxxxx"
account = w3.account.privateKeyToAccount(private_key)
addr = w3.address.encode_hex_address(account.address, w3.cfx.chain_id)
print("base32: {}".format(addr))
print(w3.cfx.get_balance(addr))

w3.cfx.default_account = account

tx = {
        # 'type': "0x1",
    'from': addr,
    'nonce': w3.cfx.get_next_nonce(addr),
    'gas': 21000,
    'to': "cfxtest:aamd4myx7f3en2yu95xye7zb78gws09gj2ykmv9p58",
    'value': 100,
    # 'maxFeePerGas': 1000000000,
    # 'maxPriorityFeePerGas': 1000000000,
    'gasPrice': 10**9,
    # 'data': b'',
    'chainId': w3.cfx.chain_id,
    'storageLimit': 0,
    'epochHeight': status['epochNumber']
}

print(tx)

signed = account.sign_transaction(tx)
rawTx = signed.rawTransaction
# print(rawTx)
w3.cfx.send_raw_transaction(rawTx)
