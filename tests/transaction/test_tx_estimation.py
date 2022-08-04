
from conflux_web3 import Web3


def test_basetx_estimate(w3: Web3, secret_key):
    """
    estimate RPC behaviour, see https://wiki.conflux123.xyz/books/conflux101/page/cfx-estimate
    """
    addr = w3.account.from_key(secret_key).address
    
    tx = {
        "from": addr,
        "to": w3.account.create().address,
        "value": 100
    }
    
    estimate = w3.cfx.estimate_gas_and_collateral(tx)
    assert estimate["gasUsed"] == 21000
    assert estimate["storageCollateralized"] == 0


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
    
   
    