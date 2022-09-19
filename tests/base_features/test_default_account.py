from conflux_web3 import Web3
from web3.datastructures import AttributeDict

def test_default_account_set(w3: Web3, secret_key):
    local_account = w3.account.from_key(secret_key)
    w3.cfx.default_account = local_account.address
    assert w3.cfx.default_account == local_account.address

    w3.cfx.default_account = local_account
    assert w3.cfx.default_account == local_account.address

    assert local_account.address in w3.wallet
    
def test_web3_connection(w3: Web3):
    assert w3.is_connected()

    # a not valid Provider
    w3_ = Web3(Web3.HTTPProvider("http://127.0.0.1:11111"))
    assert not w3_.is_connected()
