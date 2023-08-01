from typing import (
    Any,
    Callable,
    Dict,
    Union,
    Type,
    get_type_hints
)
from typing_extensions import (
    TypedDict,
)
from hexbytes import HexBytes

from eth_typing import (
    Hash32
)
from web3.datastructures import AttributeDict
from web3.types import (
    RPCEndpoint,
)
from web3._utils.method_formatters import (
    combine_formatters,
    # STANDARD_NORMALIZERS,
    to_hexbytes,
    to_hex_if_integer,
    to_integer_if_hex,
    is_not_null,
    apply_list_to_array_formatter,
)
from web3._utils.abi import (
    is_length
)
from web3._utils.normalizers import (
    abi_bytes_to_hex,
    abi_int_to_hex,
    abi_string_to_hex,
)
from web3.module import Module
from web3._utils.formatters import (
    is_array_of_dicts,
    is_array_of_strings,
    remove_key_if,
)
from web3._utils.rpc_abi import abi_request_formatters

from eth_utils.types import (
    is_dict
)

from eth_utils.toolz import (
    complement, # type: ignore
    compose,  # type: ignore
    # curried,
    partial, # type: ignore
)
from eth_utils.curried import (
    apply_formatter_at_index, # type: ignore
    apply_formatters_to_sequence,# type: ignore
    apply_formatters_to_dict,
    apply_formatter_if,
    apply_one_of_formatters,
)
from web3._utils.blocks import is_hex_encoded_block_hash as is_hash32_str

from cfx_address import (
    Base32Address
)
from conflux_web3._utils.rpc_abi import (
    RPC_ABIS,
    RPC
)
from conflux_web3.middleware.pending import (
    TransactionHash
)
from conflux_web3.types import (
    Drip,
    CollateralInfo,
)

STANDARD_NORMALIZERS = [
    abi_bytes_to_hex,
    abi_int_to_hex,
    abi_string_to_hex,
    # we only accept base32 format address
    # abi_address_to_hex, \
]

def to_hash32(val: Union[str, int, bytes], variable_length: bool=False):
    return to_hexbytes(32, val, variable_length)

def from_trust_to_base32(val: str):
    return Base32Address(val, _from_trust=True)

def from_hex_to_drip(val: Any):
    return Drip(val, 16)

transaction_param_formatter = compose(
    remove_key_if('to', lambda txn: txn['to'] in {'', b'', None}),  # type: ignore
    remove_key_if('gasPrice', lambda txn: txn['gasPrice'] in {'', b'', None}),  # type: ignore
    # transaction_request_formatter,
)

ABI_REQUEST_FORMATTERS = abi_request_formatters(STANDARD_NORMALIZERS, RPC_ABIS)

FILTER_PARAMS_FORMATTERS = {
    "fromEpoch": to_hex_if_integer,
    "toEpoch": to_hex_if_integer,
    "fromBlock": to_hex_if_integer,
    "toBlock": to_hex_if_integer,
}

PYTHONIC_REQUEST_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    # Cfx

    RPC.cfx_getBalance: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getStakingBalance: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getNextNonce: apply_formatter_at_index(to_hex_if_integer, 1),
    
    RPC.cfx_getBlockByEpochNumber: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getBlockByBlockNumber: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getBlocksByEpoch: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getSkippedBlocksByEpoch: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getBlockByHashWithPivotAssumption: apply_formatter_at_index(to_hex_if_integer, 2),
    RPC.cfx_getEpochReceipts: apply_formatter_at_index(to_hex_if_integer, 0),
    
    RPC.cfx_getCode: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getStorageAt: apply_formatter_at_index(to_hex_if_integer, 2),
    RPC.cfx_getStorageRoot: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getCollateralForStorage: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getSponsorInfo: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getAccount: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getDepositList: apply_formatter_at_index(to_hex_if_integer, 1),
    RPC.cfx_getVoteList: apply_formatter_at_index(to_hex_if_integer, 1),
    
    RPC.cfx_getInterestRate: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getAccumulateInterestRate: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getBlockRewardInfo: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getPoSEconomics: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getPoSRewardByEpoch: apply_formatter_at_index(to_hex_if_integer, 0),
    RPC.cfx_getParamsFromVote: apply_formatter_at_index(to_hex_if_integer, 0),
    # RPC.cfx_getSupplyInfo: ,
    # RPC.cfx_getAccountPendingInfo: ,
    RPC.cfx_getAccountPendingTransactions: compose(
        apply_formatter_at_index(to_hex_if_integer, 1),
        apply_formatter_at_index(to_hex_if_integer, 2),
    ),
    RPC.cfx_checkBalanceAgainstTransaction: compose(
        apply_formatter_at_index(to_hex_if_integer, 2),
        apply_formatter_at_index(to_hex_if_integer, 3),
        apply_formatter_at_index(to_hex_if_integer, 4),
        apply_formatter_at_index(to_hex_if_integer, 5),
    ),

    RPC.cfx_getLogs: apply_formatter_at_index(apply_formatters_to_dict(FILTER_PARAMS_FORMATTERS), 0),
    RPC.cfx_newFilter: apply_formatter_at_index(apply_formatters_to_dict(FILTER_PARAMS_FORMATTERS), 0),

    RPC.cfx_call: apply_one_of_formatters((
        (is_length(1), apply_formatter_at_index(transaction_param_formatter, 0)), # type: ignore
        (is_length(2), apply_formatters_to_sequence( # type: ignore
            [
                transaction_param_formatter,
                to_hex_if_integer,
            ]
        )),
    )),
    RPC.cfx_estimateGasAndCollateral: apply_one_of_formatters((
        (is_length(1), apply_formatter_at_index(transaction_param_formatter, 0)), # type: ignore
        (is_length(2), apply_formatters_to_sequence( # type: ignore
            [
                transaction_param_formatter,
                to_hex_if_integer,
            ]
        )),
    )),
    RPC.cfx_sendTransaction: apply_formatter_at_index(transaction_param_formatter, 0),
    # RPC.cfx_signTransaction: apply_formatter_at_index(transaction_param_formatter, 0),
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
    "bestHash": to_hash32,
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


LOG_ENTRY_FORMATTERS = {
    "address": from_trust_to_base32,
    "topics": apply_list_to_array_formatter(to_hash32), 
    "data": HexBytes,
    "blockHash": apply_formatter_if(is_not_null, to_hash32), 
    "epochNumber": apply_formatter_if(is_not_null, to_integer_if_hex),
    "transactionHash": apply_formatter_if(is_not_null, to_hash32), 
    "transactionIndex": apply_formatter_if(is_not_null, to_integer_if_hex),
    "logIndex": apply_formatter_if(is_not_null, to_integer_if_hex),
    "transactionLogIndex": apply_formatter_if(is_not_null, to_integer_if_hex),
}
log_entry_formatter = apply_formatters_to_dict(LOG_ENTRY_FORMATTERS)

RECEIPT_FORMATTERS = {
    "transactionHash": to_hash32, 
    "index": to_integer_if_hex,
    "blockHash": apply_formatter_if(is_not_null, to_hash32), 
    "epochNumber": to_integer_if_hex,
    "from": from_trust_to_base32,
    "to": apply_formatter_if(is_not_null, from_trust_to_base32),
    "gasUsed": to_integer_if_hex,
    "gasFee": from_hex_to_drip,
    # "gasCoveredBySponsor": bool,
    "storageCollateralized": to_integer_if_hex,
    # "storageCoveredBySponsor": bool,
    "storageReleased": apply_list_to_array_formatter(to_hex_if_integer),
    "contractCreated": apply_formatter_if(is_not_null, from_trust_to_base32),
    
    "stateRoot": to_hash32,
    "outcomeStatus": to_integer_if_hex,
    "logsBloom": to_hexbytes(256), # type: ignore
    "logs": apply_list_to_array_formatter(log_entry_formatter),
}
# receipt_formatter = apply_formatters_to_dict(RECEIPT_FORMATTERS)


TRANSACTION_DATA_FORMATTERS = {
    "blockHash": apply_formatter_if(is_not_null, to_hash32),
    "chainId": apply_formatter_if(is_not_null, to_integer_if_hex),
    "contractCreated": apply_formatter_if(is_not_null, from_trust_to_base32),
    "data": HexBytes,
    "epochHeight": apply_formatter_if(is_not_null, to_integer_if_hex),
    "from": from_trust_to_base32,
    "gas": to_integer_if_hex,
    "gasPrice": from_hex_to_drip,
    "hash": to_hash32, # 
    "nonce": to_integer_if_hex,
    "r": apply_formatter_if(is_not_null, to_hexbytes(32, variable_length=True)), # type: ignore
    "s": apply_formatter_if(is_not_null, to_hexbytes(32, variable_length=True)), # type: ignore
    "status": to_integer_if_hex,
    "storageLimit": to_integer_if_hex,
    "to": apply_formatter_if(is_not_null, from_trust_to_base32),
    "transactionIndex": apply_formatter_if(is_not_null, to_integer_if_hex),
    "v": apply_formatter_if(is_not_null, to_integer_if_hex),
    "value": from_hex_to_drip,
}
transaction_data_formatter = apply_formatters_to_dict(TRANSACTION_DATA_FORMATTERS)

filter_result_formatter = apply_one_of_formatters(
    (
        (is_array_of_dicts, apply_list_to_array_formatter(log_entry_formatter)),
        (is_array_of_strings, apply_list_to_array_formatter(to_hash32)), 
    )
)

BLOCK_FORMATTERS = {
    "hash": to_hash32,
    "parentHash": to_hash32,
    "height": to_integer_if_hex,
    "miner": from_trust_to_base32,
    "deferredStateRoot": to_hash32,
    "deferredReceiptsRoot": to_hash32,
    "deferredLogsBloomHash": to_hash32,
    "blame": to_integer_if_hex,
    "transactionsRoot": to_hash32,
    "epochNumber": apply_formatter_if(is_not_null, to_integer_if_hex),
    "blockNumber": apply_formatter_if(is_not_null, to_integer_if_hex),
    "gasLimit": to_integer_if_hex,
    "gasUsed": apply_formatter_if(is_not_null, to_integer_if_hex),
    "timestamp": to_integer_if_hex,
    "difficulty": to_integer_if_hex,
    "powQuality": apply_formatter_if(is_not_null, HexBytes),
    "refereeHashes": apply_list_to_array_formatter(to_hash32),
    # adaptive: bool
    "nonce": apply_formatter_if(is_not_null, to_hexbytes(8, variable_length=True)), # type: ignore
    "size": to_integer_if_hex,
    "custom": apply_list_to_array_formatter(HexBytes),
    "posReference": apply_formatter_if(is_not_null, to_hash32), # set for development
    "transactions": apply_one_of_formatters(
        (
            (
                is_array_of_dicts,
                apply_list_to_array_formatter(transaction_data_formatter),
            ),
            (is_array_of_strings, apply_list_to_array_formatter(to_hash32)),
        )
    )
}
block_formatter = apply_formatters_to_dict(BLOCK_FORMATTERS)


def to_transaction_hash(val: Hash32) -> TransactionHash:
    if isinstance(val, TransactionHash):
        return val
    return TransactionHash(to_hexbytes(32, val))

def fixed64_to_float(val: str) -> float:
    MAX = 2**256 - 1
    return int(val, 16) / MAX

STORAGE_ROOT_FORMATTERS = {
    "delta": apply_formatter_if(is_hash32_str, to_hash32),
    "intermediate": apply_formatter_if(is_hash32_str, to_hash32),
    "snapshot": apply_formatter_if(is_hash32_str, to_hash32),
}
storage_root_formatter = apply_formatters_to_dict(STORAGE_ROOT_FORMATTERS)

SPONSOR_INFO_FORMATTERS = {
    "sponsorBalanceForCollateral": from_hex_to_drip,
    "sponsorBalanceForGas": from_hex_to_drip,
    "sponsorGasBound": from_hex_to_drip,
    "sponsorForCollateral": from_trust_to_base32,
    "sponsorForGas": from_trust_to_base32,
    "availableStoragePoints": to_integer_if_hex,
    "usedStoragePoints": to_integer_if_hex,
}

ACCOUNT_INFO_FORMATTERS = {
    "accumulatedInterestReturn": from_hex_to_drip,
    "address": from_trust_to_base32,
    "admin": apply_formatter_if(is_not_null, from_trust_to_base32),
    "balance": from_hex_to_drip,
    "codeHash": to_hash32,
    "collateralForStorage": to_integer_if_hex,
    "nonce": to_integer_if_hex,
    "stakingBalance": from_hex_to_drip,
}

DEPOSIT_INFO_FORMATTERS = {
    "accumulatedInterestRate": to_integer_if_hex,
    "amount": from_hex_to_drip,
    "depositTime": to_integer_if_hex,
}

VOTE_INFO_FORMATTERS = {
    "amount": from_hex_to_drip,
    "unlockBlockNumber": to_integer_if_hex,
}

BLOCK_REWARD_INFO_FORMATTERS = {
    "blockHash": to_hash32,
    "author": from_trust_to_base32,
    "totalReward": from_hex_to_drip,
    "baseReward": from_hex_to_drip,
    "txFee": from_hex_to_drip,
}

POS_ECONOMICS_FORMATTERS = {
    "distributablePosInterest": from_hex_to_drip,
    "lastDistributeBlock": to_integer_if_hex,
    "totalPosStakingTokens": from_hex_to_drip,
}

POS_ACCOUNT_REWARDS_FORMATTERS = {
    # "posAddress": hexaddress
    "powAddress": from_trust_to_base32,
    "reward": from_hex_to_drip
}

POS_REWARDS_INFO_FORMATTERS = {
    "accountRewards": apply_list_to_array_formatter(
        apply_formatters_to_dict(POS_ACCOUNT_REWARDS_FORMATTERS)
    ),
    "powEpochHash": to_hash32
}

DAO_INFO_FORMATTERS = {
    "powBaseReward": from_hex_to_drip,
    "interestRate": to_integer_if_hex,
}

SUPPLY_INFO_FORMATTERS = {
    "totalCirculating": from_hex_to_drip,
    "totalCollateral": from_hex_to_drip,
    "totalIssued": from_hex_to_drip,
    "totalStaking": from_hex_to_drip,
    "totalEspaceTokens": from_hex_to_drip,
}

PENDING_INFO_FORMATTERS = {
    "localNonce": to_integer_if_hex,
    "nextPendingTx": to_hash32,
    "pendingCount": to_integer_if_hex,
    "pendingNonce": to_integer_if_hex,
}

PENDING_TRANSACTIONS_INFO_FORMATTERS = {
    "pendingCount": to_integer_if_hex,
    "pendingTransactions": apply_list_to_array_formatter(
        transaction_data_formatter
    )
}

SIMPLE_RESULT_FORMATTER_MAPPING: Dict[Type[Any], Callable[..., Any]] = {
    int: to_integer_if_hex,
    Drip: from_hex_to_drip,
    Base32Address: from_trust_to_base32,
    Hash32: to_hash32,
    HexBytes: HexBytes,
    Union[int, None]: apply_formatter_if(is_not_null, to_integer_if_hex)
}

def create_dict_result_formatter(typed_dict_class: Type[TypedDict]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    formatter_dict: Dict[str, Callable[..., Any]] = {}
    type_hints = get_type_hints(typed_dict_class)
    
    for key, type_hint in type_hints.items():
        # Get the formatter function for the specific type hint
        formatter_function = SIMPLE_RESULT_FORMATTER_MAPPING.get(type_hint, None)
        
        if formatter_function is not None:
            formatter_dict[key] = formatter_function
            
    return apply_formatters_to_dict(formatter_dict)

PYTHONIC_RESULT_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    # cfx namespace
    RPC.cfx_epochNumber: to_integer_if_hex,
    RPC.cfx_getStatus: apply_formatters_to_dict(STATUS_FORMATTERS),
    RPC.cfx_call: HexBytes,
    RPC.cfx_estimateGasAndCollateral: apply_formatters_to_dict(ESTIMATE_FORMATTERS),
    RPC.cfx_getConfirmationRiskByHash: fixed64_to_float,
    RPC.cfx_gasPrice: from_hex_to_drip,
    RPC.cfx_getBalance: from_hex_to_drip,
    RPC.cfx_getStakingBalance: from_hex_to_drip,
    RPC.cfx_getNextNonce: to_integer_if_hex,
    RPC.cfx_getBlockByHash: apply_formatter_if(is_not_null, block_formatter),
    RPC.cfx_getBlockByEpochNumber: apply_formatter_if(is_not_null, block_formatter),
    RPC.cfx_getBlockByBlockNumber: apply_formatter_if(is_not_null, block_formatter),
    RPC.cfx_getBestBlockHash: to_hash32,
    RPC.cfx_getBlocksByEpoch: apply_list_to_array_formatter(to_hash32),
    RPC.cfx_getSkippedBlocksByEpoch: apply_list_to_array_formatter(to_hash32),
    RPC.cfx_getBlockByHashWithPivotAssumption: apply_formatter_if(is_not_null, block_formatter),
    RPC.cfx_getEpochReceipts: apply_list_to_array_formatter(apply_list_to_array_formatter(apply_formatter_if(
        is_not_null,
        apply_formatters_to_dict(RECEIPT_FORMATTERS),
    ))),

    RPC.cfx_getLogs: filter_result_formatter,
    RPC.cfx_getFilterLogs: filter_result_formatter,
    RPC.cfx_getFilterChanges: filter_result_formatter,
    
    RPC.cfx_getCode: HexBytes,
    RPC.cfx_getStorageAt: apply_formatter_if(is_not_null, to_hash32),
    RPC.cfx_getStorageRoot: apply_formatter_if(is_not_null, storage_root_formatter),
    RPC.cfx_getCollateralForStorage: to_integer_if_hex,
    RPC.cfx_getSponsorInfo: apply_formatters_to_dict(SPONSOR_INFO_FORMATTERS),
    RPC.cfx_getAccount: apply_formatters_to_dict(ACCOUNT_INFO_FORMATTERS),
    RPC.cfx_getDepositList: apply_list_to_array_formatter(
        apply_formatters_to_dict(DEPOSIT_INFO_FORMATTERS)
    ),
    RPC.cfx_getVoteList: apply_list_to_array_formatter(
        apply_formatters_to_dict(VOTE_INFO_FORMATTERS)
    ),
    
    RPC.cfx_getInterestRate: to_integer_if_hex,
    RPC.cfx_getAccumulateInterestRate: to_integer_if_hex,
    RPC.cfx_getBlockRewardInfo: apply_list_to_array_formatter(
        apply_formatters_to_dict(BLOCK_REWARD_INFO_FORMATTERS)
    ),
    RPC.cfx_getPoSEconomics: apply_formatter_if(
        is_not_null, 
        apply_formatters_to_dict(POS_ECONOMICS_FORMATTERS),
    ),
    RPC.cfx_getPoSRewardByEpoch: apply_formatter_if(
        is_not_null,
        apply_formatters_to_dict(POS_REWARDS_INFO_FORMATTERS),
    ),
    RPC.cfx_getParamsFromVote: apply_formatter_if(
        is_not_null,
        apply_formatters_to_dict(DAO_INFO_FORMATTERS)
    ),
    RPC.cfx_getSupplyInfo: apply_formatters_to_dict(SUPPLY_INFO_FORMATTERS),
    RPC.cfx_getCollateralInfo: create_dict_result_formatter(CollateralInfo),

    RPC.cfx_getAccountPendingInfo: apply_formatters_to_dict(PENDING_INFO_FORMATTERS),
    RPC.cfx_getAccountPendingTransactions: apply_formatters_to_dict(PENDING_TRANSACTIONS_INFO_FORMATTERS),
    RPC.cfx_getTransactionByHash: apply_formatter_if(
        is_not_null,
        transaction_data_formatter
    ),
    # RPC.eth_getTransactionCount: to_integer_if_hex,
    RPC.cfx_getTransactionReceipt: apply_formatter_if(
        is_not_null,
        apply_formatters_to_dict(RECEIPT_FORMATTERS),
    ),
    
    RPC.cfx_sendRawTransaction: to_transaction_hash,  
    RPC.cfx_sendTransaction: to_transaction_hash,  
    # RPC.eth_sign: HexBytes,
    # RPC.eth_signTransaction: apply_formatter_if(is_not_null, signed_tx_formatter),
    # RPC.eth_signTypedData: HexBytes,
    # RPC.eth_syncing: apply_formatter_if(is_not_false, syncing_formatter),
    # # personal
    # RPC.personal_importRawKey: to_checksum_address,
    # RPC.personal_listAccounts: apply_list_to_array_formatter(to_checksum_address),
    # RPC.personal_listWallets: apply_list_to_array_formatter(geth_wallets_formatter),
    # RPC.personal_newAccount: to_checksum_address,
    # RPC.personal_sendTransaction: to_hash32,
    # RPC.personal_signTypedData: HexBytes,
    
    # Transaction Pool
    RPC.txpool_nextNonce: to_integer_if_hex,
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
