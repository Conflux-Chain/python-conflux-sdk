import pytest
from hexbytes import HexBytes
from conflux_web3 import Web3
from conflux_web3.types import BlockData
from tests._test_helpers.type_check import TypeValidator

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
        assert block_data is not None
        block_data = preprocess_block_data(block_data, use_testnet)
        return block_data
    
    @pytest.fixture
    def no_full_block_data(self, w3:Web3, block_hash: bytes, use_testnet: bool):
        block_data = w3.cfx.get_block_by_hash(block_hash, False)
        assert block_data is not None
        block_data = preprocess_block_data(block_data, use_testnet)
        return block_data
    
    def test_get_block_by_hash(self, block_data: BlockData, no_full_block_data: BlockData):
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
        for block_receipts in epoch_receipts:
            for tx_receipt in block_receipts:
                TypeValidator.validate_typed_dict(tx_receipt, "TxReceiptWithSpace")