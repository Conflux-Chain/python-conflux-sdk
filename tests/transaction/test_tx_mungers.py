import pytest
from conflux_web3 import Web3

def test_send_transaction_munger_exception(w3: Web3, address):
    
    # no "from" field
    with pytest.raises(ValueError):
        tx = {
            "to": w3.account.create().address
        }
        w3.cfx.send_transaction_munger(tx)
    try:
        # no exception here
        tx = {
            "to": w3.account.create().address
        }
        w3.cfx.default_account = address
        w3.cfx.send_transaction_munger(tx) 
        
        # no exception here
        tx = {
            "to": w3.account.create().address,
            "from": address
        }
        w3.cfx.remove_default_account()
        w3.cfx.send_transaction_munger(tx)
        
        # no exception here
        tx = tx = {
            "to": w3.account.create().address,
            "nonce": 0
        }
        w3.cfx.send_transaction_munger(tx)
    except:
        pytest.fail("unexpected error")
    
    
    
# def test_send_transaction_munger_exception(w3: Web3, Web3, address):
#     tx = {
#         "to": w3.account.create().address
#     }
#     with pytest.raises(ValueError):
#         w3.cfx.send_transaction_munger(tx)
    
    

def test_estimate_munger(w3: Web3):
    """if default_account is set, it will be set as tx's default from field
    """
    tx = {
        # "from": addr,
        # "from": w3.account.create().address,
        "to": w3.account.create().address,
        "value": 10**9
    }
    random_account = w3.account.create()
    w3.cfx.default_account = random_account.address
    
    processed = w3.cfx.estimate_gas_and_collateral_munger(tx)
    assert processed[0]['from'] == random_account.address # type: ignore 
    