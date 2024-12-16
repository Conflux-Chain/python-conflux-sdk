import os
import pytest
from typing import TYPE_CHECKING
from cfx_account.account import LocalAccount


if TYPE_CHECKING:
    from conflux_web3 import Web3

@pytest.mark.order(1)
@pytest.mark.xdist_group(name="pending")   
def test_pending(w3: "Web3", account: LocalAccount, use_testnet: bool):
    # activate by default
    # w3.middleware_onion.add(PendingTransactionMiddleware)
    addr = account.address
    w3.wallet.add_account(account)
    
    pending = w3.cfx.send_transaction({
        "from": addr, 
        "to": w3.cfx.account.create().address, 
        "value": 100,
    })
    pending.mined()
    pending.executed()
    pending.confirmed()
    if use_testnet and os.environ.get("TEST_FINALIZATION", None):
        with pytest.warns(UserWarning):
            pending.finalized()
