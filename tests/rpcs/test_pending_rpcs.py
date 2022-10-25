import pytest

from conflux_web3 import Web3

from conflux_web3.contract.metadata import get_contract_metadata
from tests._test_helpers.type_check import TypeValidator

class TestPending:
    @pytest.fixture(scope="class")
    def future_tx(self, moduled_w3: Web3):
        nonce = moduled_w3.cfx.get_next_nonce(moduled_w3.cfx.default_account)
        hash = moduled_w3.cfx.send_transaction({
            "to": moduled_w3.account.create().address,
            "value": 100,
            "nonce": nonce + 1
        })
        yield hash
        moduled_w3.cfx.send_transaction({
            "to": moduled_w3.account.create().address,
            "value": 100,
            "nonce": nonce
        })
        hash.executed()
        
    
    def test_get_account_pending_info(self, w3: Web3, address, future_tx):
        account_pending_info = w3.cfx.get_account_pending_info(address)
        TypeValidator.validate_typed_dict(account_pending_info, "PendingInfo")
    
    def test_get_account_pending_transactions(self, w3: Web3, address, future_tx):
        nonce = w3.cfx.get_next_nonce(address)
        info = w3.cfx.get_account_pending_transactions(address, nonce, 1)
        assert info["firstTxStatus"] == {"pending": "futureNonce"}
        assert info["pendingCount"] == 1
        for tx in info["pendingTransactions"]:
            TypeValidator.validate_typed_dict(tx, "TxData")
