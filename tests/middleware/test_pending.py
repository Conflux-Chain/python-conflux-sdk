from typing import TYPE_CHECKING, Sequence, cast
from cfx_account.account import LocalAccount


from conflux_web3.types import Base32Address
from conflux_web3.middleware.pending import PendingTransactionMiddleware
from tests._test_helpers.type_check import TypeValidator

if TYPE_CHECKING:
    from conflux_web3 import Web3

def test_pending(w3: "Web3", account: LocalAccount):
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
        'gasPrice': 10**9,
        'chainId': w3.cfx.chain_id,
        'storageLimit': 0,
        'epochHeight': status['epochNumber']
    }
    signed = account.sign_transaction(tx)
    rawTx = signed.rawTransaction
    pending = w3.cfx.send_raw_transaction(rawTx)
    # hash = cast(PendingTransaction, hash)
    pending.wait_till_mined()
    pending.wait_till_executed()
    pending.wait_till_confirmed()
