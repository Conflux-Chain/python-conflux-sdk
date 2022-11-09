# ## conflux-web3 code example 04: query data via RPC
# 
# Run this example online --> [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Conflux-Chain/python-conflux-sdk/dev?labpath=examples%2Fipynb%2F04-query_data_via_RPC.ipynb)

# ### Preparation

# preparation: import and init w3 instance
from conflux_web3 import Web3

# we use a new w3 object for the following presentation
w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))

# prepared constants
transaction_hash = "0x10a721e2654523a7ff682c1c8d3f868a9fdf78a3be1858bbe1f06147128d6d94"
epoch = 98943500

# ## Query via RPC
# 
# We can use SDK to invoke RPC calls to query blockchain status transaction data, block data, and so on. The full RPC document can be found [here](https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#json-rpc-methods).

# ### Query Blockchain Status

# get_status provides an overview of blockchain status
w3.cfx.get_status()

# Several RPC methods can accept an **epoch number parameter**. The epoch number parameter can be:
# * an int
# * or an epoch tag `latest_mined`, `latest_state`, `latest_confirmed` or `latest_finalized`
# 
# The concept of `epoch number` in Conflux is somewhat analogous to the concept of `block number` in other blockchains, but one epoch contains one or more blocks. Refer to https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc#the-default-epochnumber-parameter for more information.

# latest_mined epoch number
print(f"latest_mined epoch number: {w3.cfx.epoch_number}")
# get epoch number by tag
print(f'latest_state epoch numebr: {w3.cfx.epoch_number_by_tag("latest_state")}')

# ### Query Transaction

# get transaction data by hash
# this RPC is usable after transaction is sent
w3.cfx.get_transaction_by_hash(transaction_hash)

# get transaction receipt by hash
# the transaction receipt is available after it is executed
w3.cfx.get_transaction_receipt(transaction_hash)

# ### Query Block
# 
# In Conflux, each epoch contains 1 or more blocks, and one of these blocks is called `pivot` block. The pivot block determines which blocks are in the specific epoch.

# query blocks in specific epoch
block_hashes = w3.cfx.get_blocks_by_epoch(epoch)
print(f"blocks in epoch {epoch}:\n{block_hashes}")
# the last element of block_hashes is the pivot block
print(f"pivot block hash of epoch {epoch}: {block_hashes[-1].hex()}")

# if the block is a pivot block, we can get it by using epoch number
assert w3.cfx.get_block_by_epoch_number(epoch) == w3.cfx.get_block_by_hash(block_hashes[-1])

# get_block_by_epoch_number also accepts an epoch number tag
w3.cfx.get_block_by_epoch_number("latest_state")

# get a block by block number is also viable 
w3.cfx.get_block_by_block_number(110979562)

# ### Other RPCs
# 
# Besides above, `conflux-web3` supports all rpc methods under cfx Namespace. You can visit https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc#json-rpc-methods for more information.
# 
# Here are some examples:

w3.cfx.gas_price

w3.cfx.get_code("cfxtest:acejjfa80vj06j2jgtz9pngkv423fhkuxj786kjr61")

