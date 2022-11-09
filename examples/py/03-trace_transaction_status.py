# ## conflux-web3 code example 03: trace transaction status
# 
# Run this example online --> [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Conflux-Chain/python-conflux-sdk/dev?labpath=examples%2Fipynb%2F03-trace_transaction_status.ipynb)

# ### Preparation

# preparation: import and init w3 instance
from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
acct = w3.account.create()
w3.cfx.default_account = acct
faucet = w3.cfx.contract(name="Faucet")

# get a tx_hash
tx_hash = faucet.functions.claimCfx().transact()

# ## Status of a Transaction in Conflux
# 
# In Conflux, transaction will witness several period after it is sent:
# 
# 1. `pending`: the transaction is sent, but not contained in any block
# 2. `mined`: the transaction is already contained in a block, but might not be executed
# 3. `executed`: the transaction is executed
# 4. `confirmed`: the transaction is confirmed under PoW chain confirmation rule, which means it is extremly unlikely to be reverted unless the PoW chain is under attack.
# 5. `finalized`: the transaction is finalized by PoS chain, which means the transaction is impossible to revert, but it would take 5~10 minutes before a transaction is finalized.

# ## Trace the Status of a Transaction
# 
# We can use `w3.cfx.wait_till_transaction_mined`, `w3.cfx.wait_till_transaction_executed`, `w3.cfx.wait_till_transaction_confirmed`, `w3.cfx.wait_till_transaction_finalized` to wait until transaction reached specific status.

w3.cfx.wait_till_transaction_mined(tx_hash)
w3.cfx.wait_till_transaction_executed(tx_hash)
w3.cfx.wait_till_transaction_confirmed(tx_hash)
if False: # 5~10 minutes is needed
    w3.cfx.wait_till_transaction_finalized(tx_hash)

# ### Syntactic Sugar for Sent Transactions
# 
# We often need to trace the status of the sent transaction, so SDK wraps the returned hex transaction hash from `send_transacation` or `send_raw_transaction` to visit the above APIs easily.

tx_hash.mined()
tx_hash.executed()
tx_hash.confirmed()
if False:
    tx_hash.finalized()

