from conflux_web3 import Web3


def test_encode_function(w3: Web3):
    contract = w3.cfx.contract(name="ERC20", with_deployment_info=False)("0x8888888888888888888888888888888888888888")
    account = w3.cfx.account.create()
    
    assert contract.functions.transfer(account.base32_address, 1000000000000000000)._encode_transaction_data() == contract.functions.transfer(account.hex_address, 1000000000000000000)._encode_transaction_data()
    
    