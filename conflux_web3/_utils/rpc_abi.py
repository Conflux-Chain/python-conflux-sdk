from web3.types import (
    RPCEndpoint,
)

class RPC:
    # cfx
    cfx_getStatus = RPCEndpoint("cfx_getStatus")
    cfx_call = RPCEndpoint("cfx_call")
    cfx_checkBalanceAgainstTransaction = RPCEndpoint("cfx_checkBalanceAgainstTransaction")
    cfx_clientVersion = RPCEndpoint("cfx_clientVersion")
    cfx_epochNumber = RPCEndpoint("cfx_epochNumber")
    cfx_estimateGasAndCollateral = RPCEndpoint("cfx_estimateGasAndCollateral")
    cfx_gasPrice = RPCEndpoint("cfx_gasPrice")
    cfx_getAccount = RPCEndpoint("cfx_getAccount")
    cfx_getAccumulateInterestRate = RPCEndpoint("cfx_getAccumulateInterestRate")
    cfx_getAdmin = RPCEndpoint("cfx_getAdmin")
    cfx_getBalance = RPCEndpoint("cfx_getBalance")
    cfx_getBestBlockHash = RPCEndpoint("cfx_getBestBlockHash")
    cfx_getBlockByEpochNumber = RPCEndpoint("cfx_getBlockByEpochNumber")
    cfx_getBlockByBlockNumber = RPCEndpoint("cfx_getBlockByBlockNumber")
    cfx_getBlockByHash = RPCEndpoint("cfx_getBlockByHash")
    cfx_getBlockByHashWithPivotAssumption = RPCEndpoint("cfx_getBlockByHashWithPivotAssumption")
    cfx_getBlockRewardInfo = RPCEndpoint("cfx_getBlockRewardInfo")
    cfx_getBlocksByEpoch = RPCEndpoint("cfx_getBlocksByEpoch")
    cfx_getEpochReceipts = RPCEndpoint("cfx_getEpochReceipts")

    cfx_getCode = RPCEndpoint("cfx_getCode")
    cfx_getCollateralForStorage = RPCEndpoint("cfx_getCollateralForStorage")
    cfx_getConfirmationRiskByHash = RPCEndpoint("cfx_getConfirmationRiskByHash")
    cfx_getDepositList = RPCEndpoint("cfx_getDepositList")
    cfx_getInterestRate = RPCEndpoint("cfx_getInterestRate")
    cfx_getLogs = RPCEndpoint("cfx_getLogs")
    cfx_getNextNonce = RPCEndpoint("cfx_getNextNonce")
    cfx_getSkippedBlocksByEpoch = RPCEndpoint("cfx_getSkippedBlocksByEpoch")
    cfx_getSponsorInfo = RPCEndpoint("cfx_getSponsorInfo")
    cfx_getStakingBalance = RPCEndpoint("cfx_getStakingBalance")
    cfx_getStorageAt = RPCEndpoint("cfx_getStorageAt")
    cfx_getStorageRoot = RPCEndpoint("cfx_getStorageRoot")
    cfx_getTransactionByHash = RPCEndpoint("cfx_getTransactionByHash")
    cfx_getTransactionReceipt = RPCEndpoint("cfx_getTransactionReceipt")
    cfx_getVoteList = RPCEndpoint("cfx_getVoteList")
    cfx_sendRawTransaction = RPCEndpoint("cfx_sendRawTransaction")
    cfx_sendTransaction = RPCEndpoint("cfx_sendTransaction")
    
    cfx_getPoSEconomics = RPCEndpoint("cfx_getPoSEconomics")
    cfx_getPoSRewardByEpoch = RPCEndpoint("cfx_getPoSRewardByEpoch")
    cfx_getParamsFromVote = RPCEndpoint("cfx_getParamsFromVote")
    cfx_getSupplyInfo = RPCEndpoint("cfx_getSupplyInfo")
    cfx_getCollateralInfo = RPCEndpoint("cfx_getCollateralInfo")

    cfx_getAccountPendingInfo = RPCEndpoint("cfx_getAccountPendingInfo")
    cfx_getAccountPendingTransactions = RPCEndpoint("cfx_getAccountPendingTransactions")
    cfx_checkBalanceAgainstTransaction = RPCEndpoint("cfx_checkBalanceAgainstTransaction")

    cfx_newFilter = RPCEndpoint("cfx_newFilter")
    cfx_newBlockFilter = RPCEndpoint("cfx_newBlockFilter")
    cfx_newPendingTransactionFilter = RPCEndpoint("cfx_newPendingTransactionFilter")
    cfx_getFilterChanges = RPCEndpoint("cfx_getFilterChanges")
    cfx_getFilterLogs = RPCEndpoint("cfx_getFilterLogs")
    cfx_uninstallFilter = RPCEndpoint("cfx_uninstallFilter")

    # only available in LocalRPC
    cfx_getTransactionsByEpoch = RPCEndpoint("cfx_getTransactionsByEpoch")
    cfx_getTransactionsByBlock = RPCEndpoint("cfx_getTransactionsByBlock")
    
    # trace
    trace_block = RPCEndpoint("trace_block")
    trace_transaction = RPCEndpoint("trace_transaction")
    trace_epoch = RPCEndpoint("trace_epoch")

    # debug
    accounts = RPCEndpoint("accounts")
    
    # txpool
    txpool_nextNonce = RPCEndpoint("txpool_nextNonce")

    # other
    # cfx_method = RPCEndpoint("cfx_method")

TRANSACTION_PARAMS_ABIS = {
    "from": "address",
    "to": "address",
    "data": "bytes",
    "gas": "uint",
    "gasPrice": "uint",
    "nonce": "uint",
    "value": "uint",
    "chainId": "uint",
    "storageLimit": "uint",
    "epochHeight": "uint",
}

# RPC request formatters, parses abi types 
# the complex ones (None parameter, such as EpochNumberParam) are implemented in _utils.method_formatters.py

EPOCH_NUMBER_PARAM = None

RPC_ABIS = {
    RPC.cfx_call: TRANSACTION_PARAMS_ABIS,
    RPC.cfx_estimateGasAndCollateral: TRANSACTION_PARAMS_ABIS,
    RPC.cfx_getBlockByHash: ["bytes32", "bool"],
    RPC.cfx_getBlockByEpochNumber: [EPOCH_NUMBER_PARAM, "bool"],
    RPC.cfx_getBlockByBlockNumber: [EPOCH_NUMBER_PARAM, "bool"],
    RPC.cfx_getBestBlockHash: [],
    RPC.cfx_getBlocksByEpoch: [EPOCH_NUMBER_PARAM],
    RPC.cfx_getSkippedBlocksByEpoch: [EPOCH_NUMBER_PARAM],
    RPC.cfx_getBlockByHashWithPivotAssumption: ["bytes32", "bytes32", "uint"],
    RPC.cfx_getEpochReceipts: [EPOCH_NUMBER_PARAM, "bool"],

    RPC.cfx_getBalance: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getStakingBalance: ["address", EPOCH_NUMBER_PARAM],
    
    RPC.cfx_getCode: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getStorageAt: ["address", "uint", EPOCH_NUMBER_PARAM],
    RPC.cfx_getStorageRoot: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getCollateralForStorage: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getAdmin: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getSponsorInfo: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getAccount: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getDepositList: ["address", EPOCH_NUMBER_PARAM],
    RPC.cfx_getVoteList: ["address", EPOCH_NUMBER_PARAM],
    
    RPC.cfx_getInterestRate: [EPOCH_NUMBER_PARAM],
    RPC.cfx_getAccumulateInterestRate: [EPOCH_NUMBER_PARAM],
    RPC.cfx_getBlockRewardInfo: [None], # integer epoch number, or the string "latest_checkpoint"
    RPC.cfx_getPoSEconomics: [EPOCH_NUMBER_PARAM],
    RPC.cfx_getPoSRewardByEpoch: ["uint"],
    RPC.cfx_getParamsFromVote: [EPOCH_NUMBER_PARAM],
    RPC.cfx_getSupplyInfo: [],
    
    RPC.cfx_getAccountPendingInfo: ["addresss"],
    RPC.cfx_getAccountPendingTransactions: ["address", "uint", "uint"],
    RPC.cfx_checkBalanceAgainstTransaction: ["address", "address", "uint", "uint", "uint", EPOCH_NUMBER_PARAM],
    
    RPC.cfx_getTransactionByHash: ["bytes32"],
    RPC.cfx_getTransactionReceipt: ["bytes32"],
    RPC.cfx_getConfirmationRiskByHash: ["bytes32"],
    # "cfx_sendRawTransaction": ["bytes"],
    RPC.cfx_sendRawTransaction: ["bytes"],
    # "cfx_sendTransaction": TRANSACTION_PARAMS_ABIS,
    RPC.cfx_sendTransaction: TRANSACTION_PARAMS_ABIS,

    # "cfx_getLogs": FILTER_PARAMS_ABIS,
    # "cfx_signTransaction": TRANSACTION_PARAMS_ABIS,
    # "cfx_sign": ["address", "bytes"],
}
