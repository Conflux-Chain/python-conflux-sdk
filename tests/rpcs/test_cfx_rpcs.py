from hexbytes import HexBytes
import pytest

from conflux_web3 import Web3
from conflux_web3.types import BlockData
from tests._test_helpers.ENV_SETTING import erc20_metadata
from tests._test_helpers.type_check import  TypeValidator

# Note that we only test if SDK works as expected, especially for request and result formatting.
# We don't test if RPC works as expected

@pytest.fixture(scope="module")
def tx_hash(moduled_w3: Web3, secret_key) -> HexBytes:
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
    erc20 = moduled_w3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
    hash = erc20.constructor(name_="ERC20", symbol_="C", totalSupply=10**18).transact()
    contract_address = hash.executed()["contractCreated"]
    return contract_address

class TestProperty:
    def test_get_status(self, w3: Web3):
        status = w3.cfx.get_status()
        TypeValidator.validate_typed_dict(status, "NodeStatus")

    def test_chain_id(self, w3: Web3):
        assert w3.cfx.chain_id > 0

    def test_gas_price(self, w3: Web3):
        gas_price = w3.cfx.gas_price
        assert gas_price >= 10**9
        assert isinstance(gas_price, int)

    def test_client_version(self, w3: Web3):
        assert w3.cfx.client_version

class TestAccountQuery:
    def test_get_balance(self, w3: Web3, address):
        balance = w3.cfx.get_balance(address, w3.cfx.epoch_number-5)
        # the balance is supposed to be non-zero
        assert balance > 0
        # TODO: remove this part
        # if default account is set, 
        # default account is used as address default param
        # w3.cfx.default_account = address
        # default_balance = w3.cfx.get_balance()
        # assert default_balance == balance

    def test_get_balance_empty_param(self, w3: Web3):
        with pytest.raises(ValueError):
            w3.cfx.get_balance()
            
    def test_get_staking_balance(self, w3: Web3, address):
        staking_balance = w3.cfx.get_staking_balance(address, w3.cfx.epoch_number-5)
        assert staking_balance == 0
        # TODO: use staking balance contract
        
    def test_get_code(self, w3: Web3, contract_address):
        # test different cases
        # contract address / user address
        contract_code = w3.cfx.get_code(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        assert contract_code
        
        user_code = w3.cfx.get_code(w3.cfx.account.create().address)
        assert not user_code
        
    def test_get_storage_at(self, w3: Web3, contract_address, use_remote):
        # TODO: a potential bug in RPC, at present we ignore the testing in local node
        if use_remote:
            storage = w3.cfx.get_storage_at(contract_address, 100, w3.cfx.epoch_number)
            assert isinstance(storage, bytes)
        else:
            pass
        
    def test_get_storage_root(self, w3: Web3, contract_address):
        root = w3.cfx.get_storage_root(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        TypeValidator.validate_typed_dict(root, "StorageRoot")
        
        # TODO: check RPC work pattern
        # root = w3.cfx.get_storage_root(w3.account.create().address)
        # assert not root
        
    def test_get_collateral_for_storage(self, w3: Web3, address):
        storage = w3.cfx.get_collateral_for_storage(address, w3.cfx.epoch_number_by_tag("latest_state"))
        
        assert isinstance(storage, int)
    
    def test_get_sponsor_info(self, w3: Web3, contract_address):
        sponsor_info = w3.cfx.get_sponsor_info(contract_address, w3.cfx.epoch_number_by_tag("latest_state"))
        # assert sponsor_info
        TypeValidator.validate_typed_dict(sponsor_info, "SponsorInfo")
            
    def test_get_account(self, w3: Web3, address):
        account_info = w3.cfx.get_account(address, w3.cfx.epoch_number_by_tag("latest_state"))
        TypeValidator.validate_typed_dict(account_info, "AccountInfo")
    
    def test_get_deposit_list(self, w3:Web3, address):
        deposit_list = w3.cfx.get_deposit_list(address, w3.cfx.epoch_number_by_tag("latest_state"))
        for deposit_info in deposit_list:
            TypeValidator.validate_typed_dict(deposit_info, "DepositInfo")
    
    def test_get_vote_list(self, w3:Web3, address):
        vote_list = w3.cfx.get_vote_list(address, w3.cfx.epoch_number_by_tag("latest_state"))
        for vote_info in vote_list:
            TypeValidator.validate_typed_dict(vote_info, "VoteInfo")
    
class TestNonce:
    def test_get_next_nonce(self, w3: Web3, address):
        nonce = w3.cfx.get_next_nonce(address)
        assert nonce >= 0
        # if default account is set, 
        # default account is used as address default param
        # w3.cfx.default_account = address
        # default_nonce = w3.cfx.get_next_nonce()
        # assert default_nonce == nonce

    def test_get_next_nonce_empty_param(self, w3: Web3):
        with pytest.raises(ValueError):
            w3.cfx.get_next_nonce()

def test_get_tx(w3: Web3, tx_hash: HexBytes):
    """test get_transaction(_by_hash) and get_transaction_receipt
    """
    transaction_data = w3.cfx.get_transaction(tx_hash)
    # transaction not added to chain
    TypeValidator.validate_typed_dict(transaction_data, "TxData")
    transaction_receipt = w3.cfx.wait_for_transaction_receipt(tx_hash)
    # already added
    TypeValidator.validate_typed_dict(transaction_data, "TxData")
    
    # TODO: check receipt's log format
    TypeValidator.validate_typed_dict(transaction_receipt, "TxReceipt")

def test_accounts(w3: Web3, use_remote: bool):
    if use_remote:
        assert True
        return
    
    local_node_accounts = w3.cfx.accounts
    assert len(local_node_accounts) == 10

def test_get_logs(w3: Web3):
    """see test_contract
    """
    pass

def test_get_confirmation_risk(w3: Web3, tx_hash):
    blockHash = w3.cfx.wait_for_transaction_receipt(tx_hash)['blockHash']
    risk = w3.cfx.get_confirmation_risk_by_hash(blockHash)
    assert risk < 1



def preprocess_block_data(block_data, use_remote):
    if not use_remote:
        # local node may not run pos chain
        block_data = dict(block_data)
        block_data['posReference'] = HexBytes("0x0")
    return block_data

class TestBlock:
    @pytest.fixture
    def block_hash(self, w3: Web3, tx_hash):
        return w3.cfx.wait_for_transaction_receipt(tx_hash)['blockHash']
    
    @pytest.fixture
    def block_data(self, w3:Web3, block_hash, use_remote):
        block_data = w3.cfx.get_block_by_hash(block_hash, True)
        # if not use_remote:
        #     # local node may not run pos chain
        #     block_data = dict(block_data)
        #     block_data['posReference'] = HexBytes("0x0")
        block_data = preprocess_block_data(block_data, use_remote)
        return block_data
    
    @pytest.fixture
    def no_full_block_data(self, w3:Web3, block_hash, use_remote):
        block_data = w3.cfx.get_block_by_hash(block_hash, False)
        # if not use_remote:
        #     # local node may not run pos chain
        #     block_data = dict(block_data)
        #     block_data['posReference'] = HexBytes("0x0")
        block_data = preprocess_block_data(block_data, use_remote)
        return block_data
    
    def test_get_block_by_hash(self, block_data, no_full_block_data):
        # block_data is retrieved by get_block_by_hash
        TypeValidator.validate_typed_dict(block_data, "BlockData")
        TypeValidator.validate_typed_dict(no_full_block_data, "BlockData")
        return block_data

    def test_get_block_by_epoch_number(self, w3:Web3, block_data: BlockData, use_remote):
        assert block_data['epochNumber'] is not None
        data_ = w3.cfx.get_block_by_epoch_number(block_data['epochNumber'], True)
        data_ = preprocess_block_data(data_, use_remote)
        TypeValidator.validate_typed_dict(data_, "BlockData")
        
    def test_get_block_by_block_number(self, w3:Web3, block_data: BlockData, use_remote):
        assert block_data['blockNumber'] is not None
        data_ = w3.cfx.get_block_by_block_number(block_data['blockNumber'], True)
        data_ = preprocess_block_data(data_, use_remote)
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
            
    def test_get_blocks_by_hash_with_pivot_assumptions(self, w3: Web3, use_remote):
        epoch_number = w3.cfx.epoch_number_by_tag("latest_confirmed")
        blocks = w3.cfx.get_blocks_by_epoch(epoch_number)
        block_data = w3.cfx.get_block_by_hash_with_pivot_assumptions(
            blocks[0],
            blocks[-1],
            epoch_number,
        )
        block_data = preprocess_block_data(block_data, use_remote)
        TypeValidator.validate_typed_dict(block_data, "BlockData")
