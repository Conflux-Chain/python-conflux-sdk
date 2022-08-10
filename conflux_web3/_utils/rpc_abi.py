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
    cfx_getBlockByHash = RPCEndpoint("cfx_getBlockByHash")
    cfx_getBlockByHashWithPivotAssumption = RPCEndpoint("cfx_getBlockByHashWithPivotAssumption")
    cfx_getBlockRewardInfo = RPCEndpoint("cfx_getBlockRewardInfo")
    cfx_getBlocksByEpoch = RPCEndpoint("cfx_getBlocksByEpoch")
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

    # trace
    trace_block = RPCEndpoint("trace_block")
    trace_transaction = RPCEndpoint("trace_transaction")

    # debug
    accounts = RPCEndpoint("accounts")

    # other
    cfx_method = RPCEndpoint("cfx_method")

TRANSACTION_PARAMS_ABIS = {
    'from': 'address',
    'to': 'address',
    'data': 'bytes',
    'gas': 'uint',
    'gasPrice': 'uint',
    'nonce': 'uint',
    'value': 'uint',
    'chainId': 'uint',
    'storageLimit': 'uint',
    'epochHeight': 'uint',
}

RPC_ABIS = {
    'cfx_call': TRANSACTION_PARAMS_ABIS,
    'cfx_estimateGasAndCollateral': TRANSACTION_PARAMS_ABIS,
    # 'cfx_getBalance': ['address', None],
    'cfx_getBlockByHash': ['bytes32', 'bool'],
    'cfx_getCode': ['address', None],
    'cfx_getStorageAt': ['address', 'uint', None],
    'cfx_getTransactionByHash': ['bytes32'],
    'cfx_getTransactionReceipt': ['bytes32'],
    'cfx_getConfirmationRiskByHash': ['bytes32'],
    'cfx_sendRawTransaction': ['bytes'],
    'cfx_sendTransaction': TRANSACTION_PARAMS_ABIS,
    # 'cfx_getLogs': FILTER_PARAMS_ABIS,
    # 'cfx_signTransaction': TRANSACTION_PARAMS_ABIS,
    # 'cfx_sign': ['address', 'bytes'],
}