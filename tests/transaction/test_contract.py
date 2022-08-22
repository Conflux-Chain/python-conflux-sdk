from typing import cast
import pytest
from cfx_address import Base32Address
from conflux_web3 import Web3
from conflux_web3.contract import ConfluxContract
from conflux_web3.middleware.wallet import WalletMiddleware
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
            WalletMiddleware(account)
        )
        return w3

    # warnings will be raised by web3.py
    # we need to wait for web3.py to repair
    def test_contract_deploy_and_transfer(self, w3_: Web3):
        # test deployment
        erc20 = w3_.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
        hash = erc20.constructor(name_="ERC20", symbol_="C", totalSupply=10**18).transact()
        contract_address = w3_.cfx.wait_for_transaction_receipt(hash)["contractCreated"]
        assert contract_address is not None
        self.contract = w3_.cfx.contract(contract_address, abi=erc20_metadata["abi"])
        
        # test transfer
        random_account = w3_.account.create()
        hash = self.contract.functions.transfer(random_account.address, 100).transact()
        transfer_receipt = w3_.cfx.wait_for_transaction_receipt(hash)
        balance = self.contract.functions.balanceOf(random_account.address).call()
        
        assert balance == 100
        fromEpoch = transfer_receipt["epochNumber"]
        
        # test getLogs
        logs = w3_.cfx.get_logs(fromEpoch=fromEpoch)
        for log in logs:
            TypeValidator.validate_typed_dict(log, "LogReceipt")
