import pytest
from conflux_web3 import Web3
from conflux_web3.contract import ConfluxContract
from conflux_web3.middleware.wallet import Wallet
from tests._test_helpers.ENV_SETTING import erc20_metadata
from tests._test_helpers.type_check import TypeValidator

class TestERC20Contract:
    contract: ConfluxContract
    
    @pytest.fixture
    def w3_(self, w3:Web3, account):
        """w3 with wallet
        """
        w3.cfx.default_account = account
        w3.middleware_onion.add(
            Wallet(account)
        )
        return w3

    # warnings might be raised by web3.py, we just ignore these warnings
    def test_contract_deploy_and_transfer(self, w3_: Web3):
        # test deployment
        erc20 = w3_.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
        hash = erc20.constructor(name_="ERC20", symbol_="C", totalSupply=10**18).transact()
        contract_address = w3_.cfx.wait_for_transaction_receipt(hash)["contractCreated"]
        assert contract_address is not None
        contract = w3_.cfx.contract(contract_address, abi=erc20_metadata["abi"])
        
        # test transfer
        random_account = w3_.account.create()
        hash = contract.functions.transfer(random_account.address, 100).transact()
        transfer_receipt = w3_.cfx.wait_for_transaction_receipt(hash)
        balance = contract.functions.balanceOf(random_account.address).call()
        assert balance == 100
        
        # test contract caller
        balance1 = contract.caller().balanceOf(random_account.address)
        assert balance1 == 100
        
        # test getLogs
        fromEpoch = transfer_receipt["epochNumber"]
        logs = w3_.cfx.get_logs(fromEpoch=fromEpoch, address=contract_address)
        for log in logs:
            TypeValidator.validate_typed_dict(log, "LogReceipt")
            
        # test contract event
        processed_log = contract.events.Transfer.process_receipt(transfer_receipt)[0]
        assert processed_log["args"]["from"] == w3_.cfx.default_account
        assert processed_log["args"]["to"] == random_account.address
        assert processed_log["args"]["value"] == 100
        assert processed_log["blockHash"] == logs[0]["blockHash"]
        assert processed_log["epochNumber"] == logs[0]["epochNumber"]
        assert processed_log["transactionHash"] == logs[0]["transactionHash"]
        assert processed_log["transactionLogIndex"] == logs[0]["transactionLogIndex"]
        assert processed_log["transactionIndex"] == logs[0]["transactionIndex"]

        # test event filters
        filter_topics = contract.events.Transfer.get_filter_topics(
            value=100,
            to=random_account.address
        )
        assert filter_topics
        new_logs = w3_.cfx.get_logs(fromEpoch=fromEpoch, topics=filter_topics)
        assert new_logs == logs
        
        # test event get_logs
        new_processed_logs = contract.events.Transfer.get_logs(
            argument_filters={
                "value": 100,
                "to": random_account.address
            },
            fromEpoch=fromEpoch
        )
        assert new_processed_logs[0]["args"] == processed_log["args"]
