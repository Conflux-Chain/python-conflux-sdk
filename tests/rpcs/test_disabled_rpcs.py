import pytest
from conflux_web3 import Web3
from conflux_web3.exceptions import DisabledException

# Test ethereum's rpc's
# These apis are supposed to be invalid
disabled_method_list = [
    # "syncing",
    # "coinbase",
    # "mining",
    # "hashrate",
    # "block_number",
    # "max_priority_fee",
    # "get_proof",
    # "get_block",
    # "get_block_transaction_count",
    # "get_uncle_count",
    # "get_uncle_by_block",
    # "get_raw_transaction",
    # "get_raw_transaction_by_block",
    # # "get_transaction_count",
    # # "replace_transaction",
    # # "modify_transaction"
    "estimate_gas",
    # "fee_history",
    # "get_filter_changes",
    # "get_filter_logs",
    # "submit_hashrate",
    # "submit_work",
    # "uninstall_filter",
    # "get_work",
    # "generate_gas_price"
]

def test_disabled_rpcs(w3: Web3):
    for method in disabled_method_list:
        with pytest.raises(DisabledException):
            getattr(w3.cfx, method)()
            w3.cfx.estimate_gas
