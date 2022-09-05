# this example shows how to constuct a transaction from scratch
# If you are new to web3 development, we recommend you refer to the example to send transactions in examples/01_quick_start.py

import os, pprint
from conflux_web3 import Web3


web3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
account = web3.account.from_key(os.environ.get("TESTNET_SECRET"))

prebuilt_tx = {
    'from': account.address,
    'nonce': web3.cfx.get_next_nonce(account.address),
    'to': web3.account.create().address,
    'value': 100,
    'gasPrice': web3.cfx.gas_price,
    'chainId': web3.cfx.chain_id,
    # 'gas': 21000, 
    # 'storageLimit': 0,
    'epochHeight': web3.cfx.epoch_number
}

# estimate
estimate_result = web3.cfx.estimate_gas_and_collateral(prebuilt_tx)

prebuilt_tx['gas'] = estimate_result['gasLimit']
prebuilt_tx['storageLimit'] = estimate_result['storageCollateralized']

tx_receipt = web3.cfx.send_raw_transaction(
    account.sign_transaction(prebuilt_tx).rawTransaction 
).executed()
pprint.pprint(dict(tx_receipt))
