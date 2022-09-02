from conflux_web3.dev import get_testnet_web3

web3 = get_testnet_web3()

status = web3.cfx.get_status()

block_hash = "0x10a721e2654523a7ff682c1c8d3f868a9fdf78a3be1858bbe1f06147128d6d94"
transaction_hash = "0x10a721e2654523a7ff682c1c8d3f868a9fdf78a3be1858bbe1f06147128d6d94"

# get transaction data/receipt by hash
transaction_data = web3.cfx.get_transaction_by_hash(transaction_hash)
transaction_receipt = web3.cfx.get_transaction_receipt(transaction_hash)

block_data = web3.cfx.get_block_by_hash(block_hash)
# an epoch number (int) or epoch number tag (str) can be the parameter, 
# see https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc#the-default-epochnumber-parameter for more information
latest_state_block = web3.cfx.get_block_by_epoch_number("latest_state")

# besides above, conflux-web3 supports all rpc methods under cfx Namespace
# see https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc#json-rpc-methods for more information
