# ## `conflux-web3` Code Example 11: Construct Transaction from Sratch
# 
# This example shows how to constuct a transaction from scratch. If you are new to web3 development, we recommend you refer to the example to send transactions in [quickstart](./01-quickstart.ipynb).

from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
account = w3.account.from_key("0x....") # fill your secret key here

# The meaning of each field is expalained [here]()

prebuilt_tx = {
    'from': account.address,
    'nonce': w3.cfx.get_next_nonce(account.address),
    'to': w3.account.create().address,
    'value': 100,
    'gasPrice': w3.cfx.gas_price,
    'chainId': w3.cfx.chain_id,
    # 'gas': 21000, 
    # 'storageLimit': 0,
    'epochHeight': w3.cfx.epoch_number
}

# estimate
estimate_result = w3.cfx.estimate_gas_and_collateral(prebuilt_tx)

prebuilt_tx['gas'] = estimate_result['gasLimit']
prebuilt_tx['storageLimit'] = estimate_result['storageCollateralized']

w3.cfx.send_raw_transaction(
    account.sign_transaction(prebuilt_tx).rawTransaction 
).executed()

