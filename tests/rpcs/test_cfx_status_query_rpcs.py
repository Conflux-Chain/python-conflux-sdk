from conflux_web3 import Web3
from conflux_web3.types import Drip, GDrip
from tests._test_helpers.type_check import TypeValidator

class TestStatusQuery:
    def test_get_status(self, w3: Web3):
        status = w3.cfx.get_status()
        TypeValidator.validate_typed_dict(status, "NodeStatus")

    def test_chain_id(self, w3: Web3):
        assert w3.cfx.chain_id > 0

    def test_gas_price(self, w3: Web3):
        gas_price = w3.cfx.gas_price
        assert gas_price >= GDrip(1)
        assert isinstance(gas_price, Drip)

    def test_client_version(self, w3: Web3):
        assert w3.cfx.client_version
        
    def test_get_interest_rate(self, w3: Web3):
        interest_rate = w3.cfx.get_interest_rate(w3.cfx.epoch_number_by_tag("latest_state"))
        assert isinstance(interest_rate, int)
    
    def test_get_accumulate_interest_rate(self, w3: Web3):
        assert isinstance(
            w3.cfx.get_accumulate_interest_rate(w3.cfx.epoch_number_by_tag("latest_state")),
            int
        )
    
    def test_get_block_reward_info(self, w3: Web3):
        info_sequence = w3.cfx.get_block_reward_info(w3.cfx.epoch_number_by_tag("latest_checkpoint"))
        for info in info_sequence:
            TypeValidator.validate_typed_dict(info, "BlockRewardInfo")

    def test_get_pos_economics(self, w3: Web3):
        info = w3.cfx.get_pos_economics(w3.cfx.epoch_number_by_tag("latest_state"))
        TypeValidator.validate_typed_dict(info, "PoSEconomicsInfo")

    # TODO: finish this test after pos RPC finished
    # def test_get_pos_reward_by_epoch(self, w3: Web3, use_testnet: bool):
    #     if use_testnet:
    #         info = w3.cfx.get_pos_reward_by_epoch("100")
    #         TypeValidator.validate_typed_dict(info, "PoSEpochRewardInfo")

    def test_get_params_from_vote(self, w3: Web3):
        info = w3.cfx.get_params_from_vote(w3.cfx.epoch_number_by_tag("latest_state"))
        TypeValidator.validate_typed_dict(info, "DAOVoteInfo")
    
    def test_get_supply_info(self, w3: Web3):
        info = w3.cfx.get_supply_info()
        TypeValidator.validate_typed_dict(info, "SupplyInfo")
    
    def test_get_collateral_info(self, w3: Web3):
        info = w3.cfx.get_collateral_info()
        TypeValidator.validate_typed_dict(info, "CollateralInfo")
        info = w3.cfx.get_collateral_info("latest_confirmed")
        TypeValidator.validate_typed_dict(info, "CollateralInfo")
    # def test_get_account_pending_transactions(self, w3: Web3):
    #     info = 
    
    def test_get_fee_burnt(self, w3: Web3):
        fee_burnt = w3.cfx.get_fee_burnt()
        assert isinstance(fee_burnt, Drip)
