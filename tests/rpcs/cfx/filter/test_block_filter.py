import time
import pytest
from conflux_web3 import Web3
from conflux_web3.types import BlockFilterId
from tests._test_helpers.type_check import TypeValidator

class TestBlockFilter:
    @pytest.fixture(scope="class")
    def block_filter_id(self, moduled_w3: Web3) -> BlockFilterId:
        return moduled_w3.cfx.new_block_filter()

    def test_block_filter(self, moduled_w3: Web3, block_filter_id: BlockFilterId):
        time.sleep(5)
        new_blocks = moduled_w3.cfx.get_filter_changes(block_filter_id)
        assert len(new_blocks) > 0
        for block_hash in new_blocks:
            assert TypeValidator.isinstance(block_hash, bytes)
            assert len(block_hash) == 32
        assert moduled_w3.cfx.uninstall_filter(block_filter_id)