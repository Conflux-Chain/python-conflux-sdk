from typing import (
    Any,
    Callable,
    Dict,
    Union
)

from web3.datastructures import AttributeDict
from web3.types import (
    BlockIdentifier,
    CallOverrideParams,
    RPCEndpoint,
    RPCResponse,
    TReturn,
    TxParams,
    _Hash32,
)
from web3._utils.method_formatters import (
    combine_formatters,
    # STANDARD_NORMALIZERS,
    to_hexbytes,
    to_hex_if_integer,
    
)

from web3._utils.normalizers import (
    # abi_address_to_hex,
    abi_bytes_to_hex,
    abi_int_to_hex,
    abi_string_to_hex,
)
from web3.module import Module
from web3._utils.formatters import (
    hex_to_integer,
    # integer_to_hex,
    # is_array_of_dicts,
    # is_array_of_strings,
    remove_key_if,
)
from web3._utils.rpc_abi import abi_request_formatters

from eth_utils.types import (
    is_string,
    is_dict
)

from eth_utils.toolz import (
    complement, # type: ignore
    compose,  # type: ignore
    # curried,
    # partial,
)
from eth_utils.curried import (
    apply_formatter_at_index, # type: ignore
    apply_formatters_to_dict,
    apply_formatter_if,
)

from conflux_web3._utils.rpc_abi import (
    RPC_ABIS,
    RPC
)

STANDARD_NORMALIZERS = [
    abi_bytes_to_hex,
    abi_int_to_hex,
    abi_string_to_hex,
    # we only accept base32 format address
    # abi_address_to_hex, \
]

# TRANSACTION_REQUEST_FORMATTERS = {
#     'maxFeePerGas': to_hex_if_integer,
#     'maxPriorityFeePerGas': to_hex_if_integer,
# }
# transaction_request_formatter = apply_formatters_to_dict(TRANSACTION_REQUEST_FORMATTERS)
transaction_param_formatter = compose(
    remove_key_if('to', lambda txn: txn['to'] in {'', b'', None}),  # type: ignore
    remove_key_if('gasPrice', lambda txn: txn['gasPrice'] in {'', b'', None}),  # type: ignore
    # transaction_request_formatter,
)

ABI_REQUEST_FORMATTERS = abi_request_formatters(STANDARD_NORMALIZERS, RPC_ABIS)
# METHOD_NORMALIZERS: Dict[RPCEndpoint, Callable[..., Any]] = {
#     RPC.cfx_getLogs: apply_formatter_at_index(FILTER_PARAM_NORMALIZERS, 0),
#     # RPC.eth_newFilter: apply_formatter_at_index(FILTER_PARAM_NORMALIZERS, 0)
# }

to_integer_if_hex = apply_formatter_if(is_string, hex_to_integer)



PYTHONIC_REQUEST_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    # Eth
    # RPC.eth_feeHistory: compose(
    #     apply_formatter_at_index(to_hex_if_integer, 0),
    #     apply_formatter_at_index(to_hex_if_integer, 1)
    # ),
    RPC.cfx_getBalance: apply_formatter_at_index(to_hex_if_integer, 1),
    # RPC.eth_getBlockByNumber: apply_formatter_at_index(to_hex_if_integer, 0),
    # RPC.eth_getBlockTransactionCountByNumber: apply_formatter_at_index(
    #     to_hex_if_integer,
    #     0,
    # ),
    # RPC.eth_getCode: apply_formatter_at_index(to_hex_if_integer, 1),
    # RPC.eth_getStorageAt: apply_formatter_at_index(to_hex_if_integer, 2),
    # RPC.eth_getTransactionByBlockNumberAndIndex: compose(
    #     apply_formatter_at_index(to_hex_if_integer, 0),
    #     apply_formatter_at_index(to_hex_if_integer, 1),
    # ),
    # RPC.eth_getTransactionCount: apply_formatter_at_index(to_hex_if_integer, 1),
    # RPC.eth_getRawTransactionByBlockNumberAndIndex: compose(
    #     apply_formatter_at_index(to_hex_if_integer, 0),
    #     apply_formatter_at_index(to_hex_if_integer, 1),
    # ),
    # RPC.eth_getRawTransactionByBlockHashAndIndex: apply_formatter_at_index(to_hex_if_integer, 1),
    # RPC.eth_getUncleCountByBlockNumber: apply_formatter_at_index(to_hex_if_integer, 0),
    # RPC.eth_getUncleByBlockNumberAndIndex: compose(
    #     apply_formatter_at_index(to_hex_if_integer, 0),
    #     apply_formatter_at_index(to_hex_if_integer, 1),
    # ),
    # RPC.eth_getUncleByBlockHashAndIndex: apply_formatter_at_index(to_hex_if_integer, 1),
    # RPC.eth_newFilter: apply_formatter_at_index(filter_params_formatter, 0),
    # RPC.eth_getLogs: apply_formatter_at_index(filter_params_formatter, 0),
    # RPC.eth_call: apply_one_of_formatters((
    #     (is_length(2), call_without_override),
    #     (is_length(3), call_with_override),
    # )),
    # RPC.eth_estimateGas: apply_one_of_formatters((
    #     (is_length(1), estimate_gas_without_block_id),
    #     (is_length(2), estimate_gas_with_block_id),
    # )),
    RPC.cfx_sendTransaction: apply_formatter_at_index(transaction_param_formatter, 0),
    # RPC.eth_signTransaction: apply_formatter_at_index(transaction_param_formatter, 0),
    # RPC.eth_getProof: apply_formatter_at_index(to_hex_if_integer, 2),
    # # personal
    # RPC.personal_importRawKey: apply_formatter_at_index(
    #     compose(remove_0x_prefix, hexstr_if_str(to_hex)),
    #     0,
    # ),
    # RPC.personal_sign: apply_formatter_at_index(text_if_str(to_hex), 0),
    # RPC.personal_ecRecover: apply_formatter_at_index(text_if_str(to_hex), 0),
    # RPC.personal_sendTransaction: apply_formatter_at_index(transaction_param_formatter, 0),
    # # Snapshot and Revert
    # RPC.evm_revert: apply_formatter_at_index(integer_to_hex, 0),
    # RPC.trace_replayBlockTransactions: apply_formatter_at_index(to_hex_if_integer, 0),
    # RPC.trace_block: apply_formatter_at_index(to_hex_if_integer, 0),
    # RPC.trace_call: compose(
    #     apply_formatter_at_index(transaction_param_formatter, 0),
    #     apply_formatter_at_index(to_hex_if_integer, 2)
    # ),
}

STATUS_FORMATTERS = {
    # "bestHash": "0xe4bf02ad95ad5452c7676d3dfc2e57fde2a70806c2e68231c58c77cdda5b7c6c",
    "chainId": to_integer_if_hex,
    "networkId": to_integer_if_hex,
    "blockNumber": to_integer_if_hex,
    "epochNumber": to_integer_if_hex,
    "latestCheckpoint": to_integer_if_hex,
    "latestConfirmed": to_integer_if_hex,
    "latestState": to_integer_if_hex,
    "latestFinalized": to_integer_if_hex,
    "ethereumSpaceChainId": to_integer_if_hex,
    "pendingTxNumber": to_integer_if_hex
}

ESTIMATE_FORMATTERS = {
    "gasLimit": to_integer_if_hex,
    "gasUsed": to_integer_if_hex,
    "storageCollateralized": to_integer_if_hex
}


PYTHONIC_RESULT_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    # Eth
    # RPC.eth_accounts: apply_list_to_array_formatter(to_checksum_address),
    RPC.cfx_epochNumber: to_integer_if_hex,
    RPC.cfx_getStatus: apply_formatters_to_dict(STATUS_FORMATTERS),
    # RPC.eth_coinbase: to_checksum_address,
    # RPC.eth_call: HexBytes,
    RPC.cfx_estimateGasAndCollateral: apply_formatters_to_dict(ESTIMATE_FORMATTERS),
    # RPC.eth_feeHistory: fee_history_formatter,
    # RPC.eth_maxPriorityFeePerGas: to_integer_if_hex,
    RPC.cfx_gasPrice: to_integer_if_hex,
    RPC.cfx_getBalance: to_integer_if_hex,
    RPC.cfx_getNextNonce: to_integer_if_hex,
    # RPC.eth_getBlockByHash: apply_formatter_if(is_not_null, block_formatter),
    # RPC.eth_getBlockByNumber: apply_formatter_if(is_not_null, block_formatter),
    # RPC.eth_getBlockTransactionCountByHash: to_integer_if_hex,
    # RPC.eth_getBlockTransactionCountByNumber: to_integer_if_hex,
    # RPC.eth_getCode: HexBytes,
    # RPC.eth_getFilterChanges: filter_result_formatter,
    # RPC.eth_getFilterLogs: filter_result_formatter,
    # RPC.eth_getLogs: filter_result_formatter,
    # RPC.eth_getProof: apply_formatter_if(is_not_null, proof_formatter),
    # RPC.eth_getRawTransactionByBlockHashAndIndex: HexBytes,
    # RPC.eth_getRawTransactionByBlockNumberAndIndex: HexBytes,
    # RPC.eth_getRawTransactionByHash: HexBytes,
    # RPC.eth_getStorageAt: HexBytes,
    # RPC.eth_getTransactionByBlockHashAndIndex: apply_formatter_if(
    #     is_not_null,
    #     transaction_result_formatter,
    # ),
    # RPC.eth_getTransactionByBlockNumberAndIndex: apply_formatter_if(
    #     is_not_null,
    #     transaction_result_formatter,
    # ),
    # RPC.eth_getTransactionByHash: apply_formatter_if(is_not_null, transaction_result_formatter),
    # RPC.eth_getTransactionCount: to_integer_if_hex,
    # RPC.eth_getTransactionReceipt: apply_formatter_if(
    #     is_not_null,
    #     receipt_formatter,
    # ),
    # RPC.eth_getUncleCountByBlockHash: to_integer_if_hex,
    # RPC.eth_getUncleCountByBlockNumber: to_integer_if_hex,
    # RPC.eth_hashrate: to_integer_if_hex,
    # RPC.eth_protocolVersion: compose(
    #     apply_formatter_if(is_0x_prefixed, to_integer_if_hex),
    #     apply_formatter_if(is_integer, str),
    # ),
    RPC.cfx_sendRawTransaction: to_hexbytes(32),  # type: ignore
    RPC.cfx_sendTransaction: to_hexbytes(32),  # type: ignore
    # RPC.eth_sign: HexBytes,
    # RPC.eth_signTransaction: apply_formatter_if(is_not_null, signed_tx_formatter),
    # RPC.eth_signTypedData: HexBytes,
    # RPC.eth_syncing: apply_formatter_if(is_not_false, syncing_formatter),
    # # personal
    # RPC.personal_importRawKey: to_checksum_address,
    # RPC.personal_listAccounts: apply_list_to_array_formatter(to_checksum_address),
    # RPC.personal_listWallets: apply_list_to_array_formatter(geth_wallets_formatter),
    # RPC.personal_newAccount: to_checksum_address,
    # RPC.personal_sendTransaction: to_hexbytes(32),
    # RPC.personal_signTypedData: HexBytes,
    # # Transaction Pool
    # RPC.txpool_content: transaction_pool_content_formatter,
    # RPC.txpool_inspect: transaction_pool_inspect_formatter,
    # # Snapshot and Revert
    # RPC.evm_snapshot: hex_to_integer,
    # # Net
    # RPC.net_peerCount: to_integer_if_hex,
}


def cfx_request_formatters(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]]
) -> Dict[str, Callable[..., Any]]:
    request_formatter_maps = (
        ABI_REQUEST_FORMATTERS,
        # METHOD_NORMALIZERS needs to be after ABI_REQUEST_FORMATTERS
        # so that eth_getLogs's apply_formatter_at_index formatter
        # is applied to the whole address
        # rather than on the first byte of the address
        # METHOD_NORMALIZERS,
        PYTHONIC_REQUEST_FORMATTERS,
    )
    formatters = combine_formatters(request_formatter_maps, method_name)
    return compose(*formatters)


def is_attrdict(val: Any) -> bool:
    return isinstance(val, AttributeDict)
not_attrdict = complement(is_attrdict)

def cfx_result_formatters(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]],
    module: "Module",
) -> Dict[str, Callable[..., Any]]:
    formatters = combine_formatters((PYTHONIC_RESULT_FORMATTERS,), method_name)
    # formatters_requiring_module = combine_formatters(
    #     (FILTER_RESULT_FORMATTERS,), method_name
    # )

    # partial_formatters = apply_module_to_formatters(
    #     formatters_requiring_module, module, method_name
    # )
    attrdict_formatter = apply_formatter_if(
        is_dict and not_attrdict, AttributeDict.recursive
    )
    return compose(attrdict_formatter, *formatters)
