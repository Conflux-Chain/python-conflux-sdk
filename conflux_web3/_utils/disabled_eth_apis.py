from conflux_web3.exceptions import DisabledException

disabled_method_list = [
    "get_proof",
    # "get_block",
    "get_block_transaction_count",
    "get_uncle_count",
    "get_uncle_by_block",
    "get_raw_transaction",
    "get_raw_transaction_by_block",
    "get_transaction_by_block",
    # "get_transaction_count",
    # "replace_transaction",
    # "modify_transaction"
    # "estimate_gas",
    "submit_hashrate",
    "submit_work",
]

disabled_property_list = [
    "syncing",
    "coinbase",
    "mining",
    "hashrate",
    "block_number",
    "get_work",
]

disabled_list = disabled_method_list + disabled_property_list
