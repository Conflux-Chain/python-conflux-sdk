from conflux_web3 import Web3
from conflux_web3.types import Base32Address

class TestNonce:
    def test_get_next_nonce(self, w3: Web3, address: Base32Address):
        nonce = w3.cfx.get_next_nonce(address)
        assert nonce >= 0
        # if default account is set, 
        # default account is used as address default param
        # w3.cfx.default_account = address
        # default_nonce = w3.cfx.get_next_nonce()
        # assert default_nonce == nonce
    
    def test_get_transaction_count(self, w3: Web3, address: Base32Address):
        nonce = w3.cfx.get_transaction_count(address)
        assert nonce >= 0

    # def test_get_next_nonce_empty_param(self, w3: Web3, use_testnet):
    #     # TODO: remove use_testnet if statement after testnet node is repaired
    #     if use_testnet:
    #         return
    #     with pytest.raises(ValueError):
    #         w3.cfx.get_next_nonce()
