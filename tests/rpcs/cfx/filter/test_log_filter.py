import time
import pytest
from conflux_web3 import Web3
from conflux_web3.contract import ConfluxContract
from tests._test_helpers.type_check import TypeValidator

class TestLogFilter:
    @pytest.fixture(scope="class")
    def contract(self, moduled_w3: Web3):
        w3 = moduled_w3
        contract_address = w3.cfx.contract(name="ERC20").constructor(name="Coin", symbol="C", initialSupply=10**18).transact().executed()["contractCreated"]
        assert contract_address is not None
        return w3.cfx.contract(contract_address, name="ERC20")
    
    
    def test_log_filter(self, moduled_w3: Web3, contract: ConfluxContract):
        log_filter_id = moduled_w3.cfx.new_filter(address = contract.address)
        contract.functions.transfer(contract.address, 1**18).transact().executed()
        time.sleep(1)
        logs = moduled_w3.cfx.get_filter_changes(log_filter_id)
        assert len(logs) > 0
        for log in logs:
            TypeValidator.validate_typed_dict(log, "LogReceipt")
        assert moduled_w3.cfx.uninstall_filter(log_filter_id)