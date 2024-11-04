import os
import pytest
from typing import TYPE_CHECKING
from cfx_account.account import LocalAccount


if TYPE_CHECKING:
    from conflux_web3 import Web3

def test_pending(w3: "Web3", account: LocalAccount, use_testnet: bool):
    # activate by default
    # w3.middleware_onion.add(PendingTransactionMiddleware)
    
    status = w3.cfx.get_status()
    addr = account.address
    
    tx = {
        'from': addr,
        'nonce': w3.cfx.get_next_nonce(addr),
        'gas': 21000,
        'to': w3.cfx.account.create().address,
        'value': 100,
        'maxFeePerGas': 2 * w3.cfx.gas_price,
        'maxPriorityFeePerGas': 0,
        'chainId': w3.cfx.chain_id,
        'storageLimit': 0,
        'epochHeight': status['epochNumber']
    }
    signed = account.sign_transaction(tx)
    rawTx = signed.raw_transaction
    pending = w3.cfx.send_raw_transaction(rawTx)
    # hash = cast(PendingTransaction, hash)
    pending.mined()
    pending.executed()
    pending.confirmed()
    if use_testnet and os.environ.get("TEST_FINALIZATION", None):
        with pytest.warns(UserWarning):
            pending.finalized()
