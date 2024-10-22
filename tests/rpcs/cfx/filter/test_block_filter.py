import time
from conflux_web3 import Web3
from tests._test_helpers.type_check import TypeValidator

class TestBlockFilter:
    def test_block_filter(self, moduled_w3: Web3):
        block_filter_id = moduled_w3.cfx.new_block_filter()
        time.sleep(5)
        new_blocks = moduled_w3.cfx.get_filter_changes(block_filter_id)
        assert len(new_blocks) > 0
        for block_hash in new_blocks:
            assert TypeValidator.isinstance(block_hash, bytes)
            assert len(block_hash) == 32
        assert moduled_w3.cfx.uninstall_filter(block_filter_id)