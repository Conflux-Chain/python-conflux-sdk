from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Dict,
    Iterable,
    NoReturn,
    Tuple,
    Union,
)
from web3.types import (
    BlockIdentifier,
    RPCEndpoint,
    RPCResponse,
    TReturn,
    _Hash32,
)
from eth_utils.curried import (
    apply_formatter_at_index,
    apply_formatter_if,
    apply_formatter_to_array,
    apply_formatters_to_dict,
    apply_formatters_to_sequence,
    apply_one_of_formatters,
    is_0x_prefixed,
    is_address,
    is_bytes,
    is_dict,
    is_integer,
    is_null,
    is_string,
    remove_0x_prefix,
    text_if_str,
    to_checksum_address,
    to_list,
    to_tuple,
)
from web3._utils.method_formatters import (
    combine_formatters,
    compose,
    not_attrdict,
    apply_module_to_formatters,
    to_integer_if_hex,
    to_hex_if_integer,
    is_not_false,
    is_false,
    is_null,
    is_not_null,
    to_hexbytes,
    apply_list_to_array_formatter,
    is_array_of_dicts,
    is_array_of_strings,
    to_ascii_if_bytes,
)
from web3.datastructures import (
    AttributeDict,
)
from hexbytes import (
    HexBytes,
)
from conflux._utils.rpc_abi import (
    RPC,
    RPC_ABIS,
)
from web3._utils.rpc_abi import (
    abi_request_formatters,
)
from web3._utils.normalizers import (
    abi_address_to_hex,
    abi_bytes_to_hex,
    abi_int_to_hex,
    abi_string_to_hex,
)

from web3._utils.formatters import (
    integer_to_hex
)

if TYPE_CHECKING:
    from web3 import Web3  # noqa: F401
    from web3.module import (  # noqa: F401
        Module,
        ModuleV2,
    )

FILTER_RESULT_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    # RPC.eth_newPendingTransactionFilter: filter_wrapper,
    # RPC.eth_newBlockFilter: filter_wrapper,
    # RPC.eth_newFilter: filter_wrapper,
}

FILTER_PARAM_NORMALIZERS = apply_formatters_to_dict({
    'address': apply_formatter_if(is_string, lambda x: [x])
})

STANDARD_NORMALIZERS = [
    abi_bytes_to_hex,
    abi_int_to_hex,
    abi_string_to_hex,
    abi_address_to_hex,
]

STATUS_FORMATTERS = {
    'chainId': to_integer_if_hex,
    'networkId': to_integer_if_hex,
    'blockNumber': to_integer_if_hex,
    'epochNumber': to_integer_if_hex,
    'pendingTxNumber': to_integer_if_hex,
    'latestCheckpoint': to_integer_if_hex,
    'latestConfirmed': to_integer_if_hex,
    'latestState': to_integer_if_hex,
}

status_formatter = apply_formatters_to_dict(STATUS_FORMATTERS)

ACCOUNT_FORMATTERS = {
    'balance': to_integer_if_hex,
    'nonce': to_integer_if_hex,
    'stakingBalance': to_integer_if_hex,
    'collateralForStorage': to_integer_if_hex,
    'accumulatedInterestReturn': to_integer_if_hex,
}

account_formatter = apply_formatters_to_dict(ACCOUNT_FORMATTERS)

TRANSACTION_FORMATTERS = {
    'blockHash': apply_formatter_if(is_not_null, to_hexbytes(32)),
    'chainId': apply_formatter_if(is_not_null, to_integer_if_hex),
    'epochHeight': apply_formatter_if(is_not_null, to_integer_if_hex),
    'transactionIndex': apply_formatter_if(is_not_null, to_integer_if_hex),
    'nonce': to_integer_if_hex,
    'gas': to_integer_if_hex,
    'gasPrice': to_integer_if_hex,
    'storageLimit': to_integer_if_hex,
    'status': apply_formatter_if(is_not_null, to_integer_if_hex),
    'value': to_integer_if_hex,
    'publicKey': apply_formatter_if(is_not_null, to_hexbytes(64)),
    'raw': HexBytes,
    # 'from': to_checksum_address,
    # 'to': apply_formatter_if(is_address, to_checksum_address),
    'hash': to_hexbytes(32),
    'r': apply_formatter_if(is_not_null, to_hexbytes(32, variable_length=True)),
    's': apply_formatter_if(is_not_null, to_hexbytes(32, variable_length=True)),
    'v': apply_formatter_if(is_not_null, to_integer_if_hex),
}

transaction_formatter = apply_formatters_to_dict(TRANSACTION_FORMATTERS)

BLOCK_FORMATTERS = {
    'blame': to_integer_if_hex,
    'deferredReceiptsRoot': to_hexbytes(32),
    'deferredLogsBloomHash': to_hexbytes(32),
    'deferredStateRoot': to_hexbytes(32),
    'gasLimit': to_integer_if_hex,
    'powQuality': to_integer_if_hex,
    'height': to_integer_if_hex,
    'gasUsed': to_integer_if_hex,
    'size': to_integer_if_hex,
    'timestamp': to_integer_if_hex,
    'hash': apply_formatter_if(is_not_null, to_hexbytes(32)),
    'nonce': apply_formatter_if(is_not_null, to_hexbytes(8, variable_length=True)),
    # 'miner': apply_formatter_if(is_not_null, to_checksum_address),
    # 'nonce': to_integer_if_hex,
    # 'refereeHashes':  array hash
    'epochNumber': apply_formatter_if(is_not_null, to_integer_if_hex),
    'parentHash': apply_formatter_if(is_not_null, to_hexbytes(32)),
    'difficulty': to_integer_if_hex,
    'transactions': apply_one_of_formatters((
        (is_array_of_dicts, apply_list_to_array_formatter(transaction_formatter)),
        (is_array_of_strings, apply_list_to_array_formatter(to_hexbytes(32))),
    )),
    'transactionsRoot': to_hexbytes(32),
}

block_formatter = apply_formatters_to_dict(BLOCK_FORMATTERS)

LOG_ENTRY_FORMATTERS = {
    # 'address': str,
    'topics': apply_list_to_array_formatter(to_hexbytes(32)),
    'data': to_ascii_if_bytes,
}

log_entry_formatter = apply_formatters_to_dict(LOG_ENTRY_FORMATTERS)

LOG_FORMATTERS = {
    'blockHash': apply_formatter_if(is_not_null, to_hexbytes(32)),
    'epochNumber': apply_formatter_if(is_not_null, to_integer_if_hex),
    'transactionIndex': apply_formatter_if(is_not_null, to_integer_if_hex),
    'transactionLogIndex': apply_formatter_if(is_not_null, to_integer_if_hex),
    'transactionHash': apply_formatter_if(is_not_null, to_hexbytes(32)),
    'logIndex': to_integer_if_hex,
    'address': str,
    'topics': apply_list_to_array_formatter(to_hexbytes(32)),
    'data': to_ascii_if_bytes,
}

log_formatter = apply_formatters_to_dict(LOG_FORMATTERS)

logs_result_formatter = apply_list_to_array_formatter(log_entry_formatter)

STORAGE_RELEASE_FORMATTERS = {
    # 'address'
    'collaterals': to_integer_if_hex
}

storage_release_formatt = apply_formatters_to_dict(STORAGE_RELEASE_FORMATTERS)

RECEIPT_FORMATTERS = {
    'blockHash': apply_formatter_if(is_not_null, to_hexbytes(32)),
    'epochNumber': apply_formatter_if(is_not_null, to_integer_if_hex),
    'index': apply_formatter_if(is_not_null, to_integer_if_hex),
    'transactionHash': to_hexbytes(32),
    'status': to_integer_if_hex,
    'gasUsed': to_integer_if_hex,
    'outcomeStatus': to_integer_if_hex,
    'storageCollateralized': to_integer_if_hex,
    'gasFee': to_integer_if_hex,
    'contractAddress': apply_formatter_if(is_not_null, to_checksum_address),
    'logs': apply_list_to_array_formatter(log_entry_formatter),
    'logsBloom': to_hexbytes(256),
    # 'from': apply_formatter_if(is_not_null, to_checksum_address),
    # 'to': apply_formatter_if(is_address, to_checksum_address),
}

receipt_formatter = apply_formatters_to_dict(RECEIPT_FORMATTERS)

ABI_REQUEST_FORMATTERS = abi_request_formatters(STANDARD_NORMALIZERS, RPC_ABIS)

METHOD_NORMALIZERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    RPC.cfx_getLogs: apply_formatter_at_index(FILTER_PARAM_NORMALIZERS, 0),
}

FILTER_PARAMS_FORMATTERS = {
    'fromEpoch': apply_formatter_if(is_integer, integer_to_hex),
    'toEpoch': apply_formatter_if(is_integer, integer_to_hex),
    'limit': apply_formatter_if(is_integer, integer_to_hex),
}

filter_params_formatter = apply_formatters_to_dict(FILTER_PARAMS_FORMATTERS)

ESTIMATE_FORMATTERS = {
    'gasUsed': to_integer_if_hex,
    'storageCollateralized': to_integer_if_hex,
    'gasLimit': to_integer_if_hex,
}

estimate_formatter = apply_formatters_to_dict(ESTIMATE_FORMATTERS)

SPONSOR_INFO_FORMATTERS = {
    'sponsorBalanceForCollateral': to_integer_if_hex,
    'sponsorBalanceForGas': to_integer_if_hex,
    'sponsorGasBound': to_integer_if_hex,
}

sponsor_formatter = apply_formatters_to_dict(SPONSOR_INFO_FORMATTERS)

REWARD_INFO_FORMATTERS = {
    'baseReward': to_integer_if_hex,
    'totalReward': to_integer_if_hex,
    'txFee': to_integer_if_hex,
}

reward_info_formatter = apply_formatters_to_dict(REWARD_INFO_FORMATTERS)

PYTHONIC_REQUEST_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    RPC.cfx_getBalance: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getStakingBalance: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getCollateralForStorage: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getNextNonce: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getAccount: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getAdmin: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getCode: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getSponsorInfo: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getBlockByEpochNumber: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getBlocksByEpoch: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getBlockRewardInfo: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getLogs: apply_formatter_at_index(filter_params_formatter, 0),
}

PYTHONIC_RESULT_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    RPC.cfx_gasPrice: to_integer_if_hex,
    RPC.cfx_epochNumber: to_integer_if_hex,
    RPC.cfx_getBalance: to_integer_if_hex,
    RPC.cfx_getStakingBalance: to_integer_if_hex,
    RPC.cfx_getCollateralForStorage: to_integer_if_hex,
    RPC.cfx_getConfirmationRiskByHash: apply_formatter_if(is_not_null, to_integer_if_hex),
    RPC.cfx_getNextNonce: to_integer_if_hex,
    RPC.cfx_getStatus: apply_formatter_if(is_not_false, status_formatter),
    RPC.cfx_getSponsorInfo: apply_formatter_if(is_not_false, sponsor_formatter),
    RPC.cfx_getBlockRewardInfo: apply_formatter_if(is_not_false, reward_info_formatter),
    RPC.cfx_getAccount: apply_formatter_if(is_not_false, account_formatter),
    RPC.cfx_getBlockByHash: apply_formatter_if(is_not_null, block_formatter),
    RPC.cfx_getBlockByEpochNumber: apply_formatter_if(is_not_null, block_formatter),
    RPC.cfx_getTransactionByHash: apply_formatter_if(is_not_null, transaction_formatter),
    RPC.cfx_getTransactionReceipt: apply_formatter_if(is_not_null, receipt_formatter),
    RPC.cfx_getLogs: logs_result_formatter,
    RPC.cfx_estimateGasAndCollateral: apply_formatter_if(is_not_null, estimate_formatter),
    RPC.cfx_sendRawTransaction: to_hexbytes(32),
    RPC.cfx_sendTransaction: to_hexbytes(32),
}

def get_request_formatters(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]]
) -> Dict[str, Callable[..., Any]]:
    request_formatter_maps = (
        ABI_REQUEST_FORMATTERS,
        # METHOD_NORMALIZERS needs to be after ABI_REQUEST_FORMATTERS
        # so that eth_getLogs's apply_formatter_at_index formatter
        # is applied to the whole address
        # rather than on the first byte of the address
        METHOD_NORMALIZERS,
        PYTHONIC_REQUEST_FORMATTERS,
    )
    formatters = combine_formatters(request_formatter_maps, method_name)
    return compose(*formatters)


def get_result_formatters(
    method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]],
    module: Union["Module", "ModuleV2"],
) -> Dict[str, Callable[..., Any]]:
    formatters = combine_formatters(
        (PYTHONIC_RESULT_FORMATTERS,),
        method_name
    )
    formatters_requiring_module = combine_formatters(
        (FILTER_RESULT_FORMATTERS,),
        method_name
    )

    partial_formatters = apply_module_to_formatters(
        formatters_requiring_module,
        module,
        method_name
    )
    attrdict_formatter = apply_formatter_if(is_dict and not_attrdict, AttributeDict.recursive)
    return compose(*partial_formatters, attrdict_formatter, *formatters)