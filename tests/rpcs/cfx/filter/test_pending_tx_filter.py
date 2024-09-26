import pytest
from conflux_web3 import Web3
from conflux_web3.types import Drip, TxFilterId
from tests._test_helpers.type_check import TypeValidator

class TestPendingTxFilter:
    @pytest.fixture(scope="class")
    def pending_tx_filter_id(self, moduled_w3: Web3) -> TxFilterId:
        return moduled_w3.cfx.new_pending_transaction_filter()

    def test_pending_tx_filter(self, moduled_w3: Web3, pending_tx_filter_id: TxFilterId):
        constucted_pending_tx = moduled_w3.cfx.send_transaction({
            "to": moduled_w3.address.zero_address(),
            "value": Drip(100),
        })
        pending_txs = moduled_w3.cfx.get_filter_changes(pending_tx_filter_id)
        assert len(pending_txs) > 0
        for pending_tx in pending_txs:
            assert TypeValidator.isinstance(pending_tx, bytes)
            assert len(pending_tx) == 32
        
        constucted_pending_tx.executed()
        assert moduled_w3.cfx.uninstall_filter(pending_tx_filter_id)