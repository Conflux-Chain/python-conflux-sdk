from hexbytes import HexBytes
import time, pytest

from cfx_address import Base32Address
from cfx_account import LocalAccount
from conflux_web3 import Web3
from conflux_web3.contract import ConfluxContract
from conflux_web3.types import (
    BlockData,
    Drip,
    GDrip,
    BlockFilterId,
    TxFilterId,
    LogFilterId,
)
from conflux_web3.contract.metadata import get_contract_metadata
from tests._test_helpers.type_check import TypeValidator

# Note that we only test if SDK works as expected, especially for request and result formatting.
# We don't test if RPC works as expected

@pytest.fixture(scope="module")
def tx_hash(moduled_w3: Web3, secret_key: str) -> HexBytes:
    w3 = moduled_w3
    status = w3.cfx.get_status()
    account = w3.account.from_key(secret_key)
    addr = account.address
    
    tx = {
        'from': addr,
        'nonce': w3.cfx.get_next_nonce(addr),
        'gas': 21000,
        'to': "cfxtest:aamd4myx7f3en2yu95xye7zb78gws09gj2ykmv9p58",
        'value': 100,
        'gasPrice': 10**9,
        'chainId': w3.cfx.chain_id,
        'storageLimit': 0,
        'epochHeight': status['epochNumber']
    }
    signed = account.sign_transaction(tx)
    rawTx = signed.rawTransaction
    h = w3.cfx.send_raw_transaction(rawTx)
    h.executed()
    return h

@pytest.fixture(scope="module")
def contract_address(moduled_w3: Web3):
    erc20_metadata = get_contract_metadata("ERC20")
    erc20 = moduled_w3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
    hash = erc20.constructor(name="Coin", symbol="C", initialSupply=10**18).transact()
    contract_address = hash.executed()["contractCreated"]
    return contract_address

@pytest.fixture(scope="module")
def tx_with_log(moduled_w3: Web3, contract_address: Base32Address) -> HexBytes:
    w3 = moduled_w3
    erc20_metadata = get_contract_metadata("ERC20")
    erc20 = w3.cfx.contract(address=contract_address, abi=erc20_metadata["abi"])

    hash = erc20.functions.transfer(w3.account.create().address, 100).transact()
    hash.executed()
    return hash

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
        assert not user_code
    
    def test_get_admin(self, w3: Web3, contract_address: Base32Address):
        # test different cases
        # contract address / user address
        contract_code = w3.cfx.get_admin(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        assert isinstance(contract_code, Base32Address) # reorg might happen, so we only assert the variable type
        
        user_admin = w3.cfx.get_code(w3.cfx.account.create().address)
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

def test_get_tx(moduled_w3: Web3, contract_address: Base32Address):
    """test get_transaction(_by_hash) and get_transaction_receipt
    """
    w3 = moduled_w3
    erc20_metadata = get_contract_metadata("ERC20")
    erc20 = w3.cfx.contract(address=contract_address, abi=erc20_metadata["abi"])

    tx_hash = erc20.functions.transfer(w3.account.create().address, 100).transact()
    transaction_data = w3.cfx.get_transaction(tx_hash)
    # transaction not added to chain
    TypeValidator.validate_typed_dict(transaction_data, "TxData")
    transaction_receipt = w3.cfx.wait_for_transaction_receipt(tx_hash)
    # already added
    TypeValidator.validate_typed_dict(transaction_data, "TxData")

    TypeValidator.validate_typed_dict(transaction_receipt, "TxReceipt")

def test_accounts(w3: Web3, use_testnet: bool):
    if use_testnet:
        assert True
        return
    
    local_node_accounts = w3.cfx.accounts
    assert len(local_node_accounts) == 10

def test_get_logs(w3: Web3):
    """see test_contract
    """
    pass

def test_get_confirmation_risk(w3: Web3, tx_hash: HexBytes):
    blockHash = w3.cfx.wait_for_transaction_receipt(tx_hash)['blockHash']
    risk = w3.cfx.get_confirmation_risk_by_hash(blockHash)
    assert risk < 1

def preprocess_block_data(block_data: BlockData, use_testnet: bool) -> BlockData:
    """
    preprocess block in local testnet
    """    
    if not use_testnet:
        # local node may not run pos chain
        block_data = dict(block_data) # type: ignore
        block_data['posReference'] = HexBytes("0x0") # type: ignore
    return block_data

class TestBlock:
    @pytest.fixture
    def block_hash(self, w3: Web3, tx_hash: HexBytes):
        return w3.cfx.wait_for_transaction_receipt(tx_hash)['blockHash']
    
    @pytest.fixture
    def block_data(self, w3:Web3, block_hash: bytes, use_testnet: bool):
        block_data = w3.cfx.get_block_by_hash(block_hash, True)
        # if not use_testnet:
        #     # local node may not run pos chain
        #     block_data = dict(block_data)
        #     block_data['posReference'] = HexBytes("0x0")
        assert block_data is not None
        block_data = preprocess_block_data(block_data, use_testnet)
        return block_data
    
    @pytest.fixture
    def no_full_block_data(self, w3:Web3, block_hash: bytes, use_testnet: bool):
        block_data = w3.cfx.get_block_by_hash(block_hash, False)
        # if not use_testnet:
        #     # local node may not run pos chain
        #     block_data = dict(block_data)
        #     block_data['posReference'] = HexBytes("0x0")
        assert block_data is not None
        block_data = preprocess_block_data(block_data, use_testnet)
        return block_data
    
    def test_get_block_by_hash(self, block_data: BlockData, no_full_block_data: BlockData):
        # block_data is retrieved by get_block_by_hash
        TypeValidator.validate_typed_dict(block_data, "BlockData")
        TypeValidator.validate_typed_dict(no_full_block_data, "BlockData")
        return block_data

    def test_get_block_by_epoch_number(self, w3:Web3, block_data: BlockData, use_testnet: bool):
        assert block_data['epochNumber'] is not None
        data_ = w3.cfx.get_block_by_epoch_number(block_data['epochNumber'], True)
        data_ = preprocess_block_data(data_, use_testnet)
        TypeValidator.validate_typed_dict(data_, "BlockData")
        
    def test_get_block_by_block_number(self, w3:Web3, block_data: BlockData, use_testnet: bool):
        assert block_data['blockNumber'] is not None
        data_ = w3.cfx.get_block_by_block_number(block_data['blockNumber'], True)
        data_ = preprocess_block_data(data_, use_testnet)
        assert dict(data_) == dict(block_data)

    def test_get_best_block_hash(self, w3:Web3):
        best_block_hash = w3.cfx.get_best_block_hash()
        assert isinstance(best_block_hash, HexBytes)
        
    def test_get_blocks_by_epoch(self, w3: Web3):
        blocks = w3.cfx.get_blocks_by_epoch("latest_state")
        for block_hash in blocks:
            assert isinstance(block_hash, bytes)
            
    def test_get_skipped_blocks(self, w3: Web3):
        # TODO: do check if blocks is not empty
        blocks = w3.cfx.get_skipped_blocks_by_epoch("latest_state")
        for block_hash in blocks:
            assert isinstance(block_hash, bytes)
            
    def test_get_blocks_by_hash_with_pivot_assumptions(self, w3: Web3, use_testnet: bool):
        epoch_number = w3.cfx.epoch_number_by_tag("latest_confirmed")
        blocks = w3.cfx.get_blocks_by_epoch(epoch_number)
        block_data = w3.cfx.get_block_by_hash_with_pivot_assumptions(
            blocks[0],
            blocks[-1],
            epoch_number,
        )
        block_data = preprocess_block_data(block_data, use_testnet)
        TypeValidator.validate_typed_dict(block_data, "BlockData")

    def test_get_block(self, w3: Web3, block_data: BlockData, use_testnet: bool):
        epoch_number = block_data["epochNumber"]
        assert epoch_number is not None
        hash = block_data["hash"]
        str_hash = hash.hex()
        for block_identifier in [epoch_number, str_hash, hash, "latest_state"]:
            block = w3.cfx.get_block(block_identifier)
            block = preprocess_block_data(block, use_testnet)
            TypeValidator.validate_typed_dict(block, "BlockData")
    
    def test_epoch_receipts(self, w3: Web3, block_data: BlockData):
        epoch_number = block_data["epochNumber"]
        assert epoch_number is not None
        epoch_receipts = w3.cfx.get_epoch_receipts(epoch_number, True)
        # assert epoch is not None
        for block_receipts in epoch_receipts:
            for tx_receipt in block_receipts:
                TypeValidator.validate_typed_dict(tx_receipt, "TxReceiptWithSpace")

def test_check_balance_against_transaction(w3: Web3, address: Base32Address, contract_address: Base32Address):
    payment_info = w3.cfx.check_balance_against_transaction(
        address, contract_address, 10000, 10**9, 0, w3.cfx.epoch_number_by_tag("latest_state")
    )
    TypeValidator.validate_typed_dict(payment_info, "TransactionPaymentInfo")
    payment_info = w3.cfx.check_balance_against_transaction(
        address, contract_address, 10000, GDrip(1), 0, w3.cfx.epoch_number_by_tag("latest_state")
    )
    TypeValidator.validate_typed_dict(payment_info, "TransactionPaymentInfo")

class TestBlockFilter:
    @pytest.fixture(scope="class")
    def block_filter_id(self, moduled_w3: Web3) -> BlockFilterId:
        return moduled_w3.cfx.new_block_filter()

    def test_block_filter(self, moduled_w3: Web3, block_filter_id: BlockFilterId):
        time.sleep(5)
        new_blocks = moduled_w3.cfx.get_filter_changes(block_filter_id)
        # new_blocks = moduled_w3.manager.request_blocking(
        #     "cfx_getFilterChanges", [block_filter_id]
        # )
        assert len(new_blocks) > 0
        for block_hash in new_blocks:
            assert TypeValidator.isinstance(block_hash, bytes)
            assert len(block_hash) == 32
        assert moduled_w3.cfx.uninstall_filter(block_filter_id)


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


class TestLogFilter:
    @pytest.fixture(scope="class")
    def contract(self, moduled_w3: Web3):
        w3 = moduled_w3
        contract_address = w3.cfx.contract(name="ERC20").constructor(name="Coin", symbol="C", initialSupply=10**18).transact().executed()["contractCreated"]
        assert contract_address is not None
        return w3.cfx.contract(contract_address, name="ERC20")
    
    @pytest.fixture(scope="class")
    def log_filter_id(self, moduled_w3: Web3, contract: ConfluxContract):
        return moduled_w3.cfx.new_filter(address = contract.address)
    
    def test_log_filter(self, moduled_w3: Web3, contract: ConfluxContract, log_filter_id: LogFilterId):
        contract.functions.transfer(contract.address, 1**18).transact().executed()
        time.sleep(1)
        logs = moduled_w3.cfx.get_filter_changes(log_filter_id)
        assert len(logs) > 0
        for log in logs:
            TypeValidator.validate_typed_dict(log, "LogReceipt")
        assert moduled_w3.cfx.uninstall_filter(log_filter_id)
