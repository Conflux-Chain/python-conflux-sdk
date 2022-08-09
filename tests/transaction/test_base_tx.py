from typing import Sequence
from cfx_account.account import LocalAccount
from conflux_web3 import Web3
from conflux_web3.types import Base32Address
from tests._test_helpers.type_check import TypeValidator

def test_send_raw_transaction(w3: Web3, account: LocalAccount):
    status = w3.cfx.get_status()
    
    addr = account.address
    
    tx = {
        'from': addr,
        'nonce': w3.cfx.get_next_nonce(addr),
        'gas': 21000,
        'to': "cfxtest:aamd4myx7f3en2yu95xye7zb78gws09gj2ykmv9p58",
        'value': 100,
        'gasPrice': 10**9,
        'chainId': w3.cfx.chain_id,
        'storageLimit': 0,
        'epochHeight': status['epochNumber']
    }
    signed = account.sign_transaction(tx)
    rawTx = signed.rawTransaction
    r = w3.cfx.send_raw_transaction(rawTx)
    assert isinstance(r, bytes)
    w3.cfx.wait_for_transaction_receipt(r)

def test_basetx_estimate(w3: Web3, address: Base32Address):
    """
    estimate RPC behaviour, see https://wiki.conflux123.xyz/books/conflux101/page/cfx-estimate
    """
    # addr = w3.account.from_key(secret_key).address
    
    tx = {
        "from": address,
        "to": w3.account.create().address,
        "value": 100
    }
    
    estimate = w3.cfx.estimate_gas_and_collateral(tx)
    assert estimate.gasUsed == 21000
    assert estimate["storageCollateralized"] == 0
    TypeValidator.validate_estimate(estimate)

def test_send_transaction(w3: Web3, embedded_accounts: Sequence[Base32Address]):
    """test "cfx_sendTransaction"
    only works for local node if no middleware is activated
    """
    # check if is a local node
    if len(embedded_accounts) == 0:
        return
    tx = {
        'from': embedded_accounts[0],
        # 'nonce': w3.cfx.get_next_nonce(addr),
        # 'gas': 21000,
        'to': w3.cfx.account.create().address,
        'value': 100,
        # 'gasPrice': 10**9,
        # 'chainId': w3.cfx.chain_id,
        # 'storageLimit': 0,
        # 'epochHeight': status['epochNumber']
    }
    
    hash = w3.cfx.send_transaction(tx)
    assert hash
    w3.cfx.wait_for_transaction_receipt(hash)
