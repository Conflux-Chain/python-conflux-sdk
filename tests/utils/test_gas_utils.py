from conflux_web3 import Web3

def test_generate_gas_price(w3: Web3):
    assert w3.cfx.generate_gas_price() is None
