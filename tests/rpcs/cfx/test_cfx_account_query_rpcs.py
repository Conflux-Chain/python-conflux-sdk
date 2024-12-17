from hexbytes import HexBytes
import pytest
from conflux_web3 import Web3
from conflux_web3.types import Base32Address, Drip
from tests._test_helpers.type_check import TypeValidator

class TestAccountQuery:
    
    def test_get_balance(self, w3: Web3, address: Base32Address):
        balance = w3.cfx.get_balance(address, w3.cfx.epoch_number-5)
        # the balance is supposed to be non-zero
        assert balance > 0
        assert isinstance(balance, Drip)

    # def test_get_balance_empty_param(self, w3: Web3, use_testnet):
    #     # TODO: remove use_testnet if statement after testnet node is repaired
    #     if use_testnet:
    #         return
    #     with pytest.raises(TypeError):
    #         w3.cfx.get_balance()
            
    
    def test_get_staking_balance(self, w3: Web3, address: Base32Address):
        staking_balance = w3.cfx.get_staking_balance(address, w3.cfx.epoch_number-5)
        assert staking_balance >= 0
        assert isinstance(staking_balance, Drip)
        # TODO: use staking balance contract

    
    def test_get_code(self, w3: Web3, contract_address: Base32Address):
        # test different cases
        # contract address / user address
        contract_code = w3.cfx.get_code(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        assert isinstance(contract_code, bytes) # reorg might happen, so we only assert the variable type
        
        user_code = w3.cfx.get_code(w3.cfx.account.create().address)
        assert user_code == HexBytes("0x")
    
    
    def test_get_admin(self, w3: Web3, contract_address: Base32Address):
        # test different cases
        # contract address / user address
        contract_code = w3.cfx.get_admin(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        assert isinstance(contract_code, Base32Address) # reorg might happen, so we only assert the variable type
        
        random_contract_address = w3.address(w3.cfx.account.create().address.replace("0x8", "0x1"))
        user_admin = w3.cfx.get_admin(random_contract_address)
        assert user_admin is None
        
    
    def test_get_storage_at(self, w3: Web3, contract_address: Base32Address, use_testnet: bool):
        # TODO: a potential bug in RPC, at present we ignore the testing in local node
        if use_testnet:
            storage = w3.cfx.get_storage_at(contract_address, 100, w3.cfx.epoch_number_by_tag("latest_state"))
            assert isinstance(storage, bytes)
        else:
            pass
        
    
    def test_get_storage_root(self, w3: Web3, contract_address: Base32Address):
        root = w3.cfx.get_storage_root(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        TypeValidator.validate_typed_dict(root, "StorageRoot")
        
        # TODO: check RPC work pattern
        # root = w3.cfx.get_storage_root(w3.account.create().address)
        # assert not root

    
    def test_get_collateral_for_storage(self, w3: Web3, address: Base32Address):
        storage = w3.cfx.get_collateral_for_storage(address, w3.cfx.epoch_number_by_tag("latest_state"))
        
        assert isinstance(storage, int)
    
    
    def test_get_sponsor_info(self, w3: Web3, contract_address: Base32Address):
        sponsor_info = w3.cfx.get_sponsor_info(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        # assert sponsor_info
        TypeValidator.validate_typed_dict(sponsor_info, "SponsorInfo")

    
    def test_get_account(self, w3: Web3, address: Base32Address):
        account_info = w3.cfx.get_account(address, w3.cfx.epoch_number_by_tag("latest_state"))
        TypeValidator.validate_typed_dict(account_info, "AccountInfo")

    
    def test_get_deposit_list(self, w3:Web3, address: Base32Address):
        deposit_list = w3.cfx.get_deposit_list(address)
        for deposit_info in deposit_list:
            TypeValidator.validate_typed_dict(deposit_info, "DepositInfo")
    
    
    def test_get_vote_list(self, w3:Web3, address: Base32Address):
        vote_list = w3.cfx.get_vote_list(address, w3.cfx.epoch_number_by_tag("latest_state"))
        for vote_info in vote_list:
            TypeValidator.validate_typed_dict(vote_info, "VoteInfo")
    