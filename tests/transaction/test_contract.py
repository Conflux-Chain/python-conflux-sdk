from typing import TYPE_CHECKING
import os, json, pytest
from conflux_web3 import Web3
from conflux_web3.contract import (
    ConfluxContract,
)
from conflux_web3.contract.metadata import (
    get_contract_metadata
)
from cfx_utils.exceptions import Base32AddressNotMatch
from conflux_web3.middleware.wallet import Wallet
from cfx_account import LocalAccount
from tests._test_helpers.type_check import TypeValidator
from web3.exceptions import ValidationError

if TYPE_CHECKING:
    from conflux_web3 import Web3

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
        erc20_metadata = get_contract_metadata("ERC20")
        erc20 = w3_.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
        hash = erc20.constructor(name="Coin", symbol="C", initialSupply=10**18).transact()
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
        assert processed_log["args"]["from"] == w3_.cfx.default_account, processed_log
        assert processed_log["args"]["to"] == random_account.address, processed_log
        assert processed_log["args"]["value"] == 100, processed_log
        assert processed_log["blockHash"] == logs[0]["blockHash"], processed_log
        assert processed_log["epochNumber"] == logs[0]["epochNumber"], processed_log
        assert processed_log["transactionHash"] == logs[0]["transactionHash"], processed_log
        assert processed_log["transactionLogIndex"] == logs[0]["transactionLogIndex"], processed_log
        assert processed_log["transactionIndex"] == logs[0]["transactionIndex"], processed_log

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

    def test_contract_without_wallet(self, w3: Web3, account: LocalAccount):
        erc20_metadata = get_contract_metadata("ERC20")
        
        erc20 = w3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
        # test raw
        prebuilt_tx_params = erc20.constructor(name="Coin", symbol="C", initialSupply=10**18).build_transaction({
            'from': account.address,
            # 'nonce': w3.cfx.get_next_nonce(account.address),
            # 'value': 0,
            # 'gas': 21000,
            # 'gasPrice': 10**9,
            # 'chainId': w3.cfx.chain_id,
            # 'epochHeight': w3.cfx.epoch_number
        })
        
        raw_constuct_tx = account.sign_transaction(prebuilt_tx_params).rawTransaction
        contract_address = w3.cfx.send_raw_transaction(raw_constuct_tx).executed()["contractCreated"]
        assert contract_address
        
        contract_instance = w3.cfx.contract(address=contract_address, abi=erc20_metadata["abi"])
        prebuilt_transfer = contract_instance.functions.transfer(
            w3.account.create().address,
            100
        ).build_transaction({
            'from': account.address
        })
        raw_tx = account.sign_transaction(prebuilt_transfer).rawTransaction
        w3.cfx.send_raw_transaction(raw_tx).executed()
        
class TestEmbeddedContractMetadata:
    def test_get_contract_metadata(self):
        admin_contract_metadata = get_contract_metadata("AdminControl")
        assert isinstance(admin_contract_metadata["abi"], list)
        assert isinstance(admin_contract_metadata, dict)

    def test_contract_from_metadata(self, w3: Web3, use_testnet: bool):
        admin_contract = w3.cfx.contract(**get_contract_metadata("AdminControl"))
        assert admin_contract.abi
        assert w3.cfx.address.is_valid_base32(admin_contract.address)
        
        if use_testnet:
            
            usdt_contract = w3.cfx.contract(**get_contract_metadata("cUSDT", w3.cfx.chain_id))
            assert usdt_contract.abi
            assert usdt_contract.bytecode
            assert w3.cfx.address.is_valid_base32(usdt_contract.address)
            assert usdt_contract.caller.symbol() == "cUSDT"
            
    def test_contract_from_name(self, w3: Web3, use_testnet: bool):
        admin_contract = w3.cfx.contract(name="AdminControl")
        assert admin_contract.abi
        assert w3.cfx.address.is_valid_base32(admin_contract.address)
        
        if use_testnet:
            usdt_contract = w3.cfx.contract(name="cUSDT")
            assert usdt_contract.abi
            assert usdt_contract.bytecode
            assert w3.cfx.address.is_valid_base32(usdt_contract.address)
            assert usdt_contract.caller.symbol() == "cUSDT"
            
        if w3.cfx.chain_id == 1:
            faucet = w3.cfx.contract(name="Faucet")
            assert faucet
    
    # TODO: test all embedded metadata functionalities
    def test_faucet_functions(self, w3: Web3):
        if w3.cfx.chain_id == 1:
            random_account = w3.account.create()
            w3.cfx.default_account = random_account
            faucet = w3.cfx.contract(name="Faucet")
            faucet.functions.claimCfx().transact().executed()
            assert w3.cfx.get_balance(w3.cfx.default_account) > 0
            

def test_contract_initialization(w3: Web3):
    metadata = get_contract_metadata("AdminControl")
    chain_id = w3.cfx.chain_id
    metadata["address"] = w3.cfx.address(metadata["address"], chain_id+1)
    
    with pytest.raises(Base32AddressNotMatch):
        w3.cfx.contract(**metadata)

def test_contract_with_no_deployment_info(w3: Web3):
    c = w3.cfx.contract(name="AdminControl", with_deployment_info=False)
    assert not c.address

def test_get_function_by_signature(w3: Web3, account: LocalAccount):
    from tests._test_helpers.ENV_SETTING import HELPER_DIR
    with open(os.path.join(HELPER_DIR, "amb_metadata.json")) as f:
        metadata = json.load(f)
    contract = w3.cfx.contract(abi=metadata['abi'], bytecode=metadata["bytecode"])
    with pytest.raises(ValidationError):
        contract.functions.identity("123456", True)
    
    w3.cfx.default_account = account
    contract_addr = contract.constructor().transact().executed()["contractCreated"]
    assert contract_addr
    contract = contract(contract_addr)
    func = contract.get_function_by_signature('identity(uint256,bool)')
    assert func(123456, True).call() == 123456
