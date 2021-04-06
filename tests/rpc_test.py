from web3.providers import HTTPProvider
from conflux import Conflux
from cfx_account.account import Account
from hexbytes import (
    HexBytes,
)

def print_fields(item):
    for key in item:
        value = item[key]
        if isinstance(value, HexBytes):
            value = value.hex()
        print(key, ':', value)


conflux_testnet_rpc = 'https://testnet-rpc.conflux-chain.org.cn/v2'
provider = HTTPProvider(conflux_testnet_rpc)
conflux = Conflux(provider)
account = "cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da"
tx_hash = "0xbe2a7cafb652f4c95a8a6fb3f2dc72ec9ff914fe27bcd1280b6be905481e5473"
block_hash = "0x573f11c723e98cfbdbfcc3d32b1d6b55d5e2d94082e13ede1866dc47ddda2359"
epoch_number = 19978013
private_key = '0xcc7939276283a32f60d2fad7d16cac972300308fe99ec98d0e63765d02e24863'
address = 'cfxtest:aar3uh6bm4hr5bb73rrya99u5y1cm2pgeja196rfeb'
key_account = Account.from_key(private_key)

txinfo = {
    "from": address,
    "to": "cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da",
    "value": 10
}

block_fields = [
    "adaptive",
    "blame",
    "deferredLogsBloomHash",
    "deferredReceiptsRoot",
    "deferredStateRoot",
    "difficulty",
    "epochNumber",
    "gasLimit",
    "gasUsed",
    "hash",
    "height",
    "miner",
    "nonce",
    "parentHash",
    "powQuality",
    "refereeHashes",
    "size",
    "timestamp",
    "transactions",
    "transactionsRoot"
]

tx_fields = [
    'blockHash',
    'chainId',
    'contractCreated',
    'data',
    'epochHeight',
    'from',
    'gas',
    'gasPrice',
    'hash',
    'nonce',
    'r', 's', 'v',
    'status',
    'storageLimit',
    'to',
    'transactionIndex',
    'value'
]

receipt_fields = [
    'transactionHash',
    'index',
    'blockHash',
    'epochNumber',
    'from', 'to',
    'gasUsed', 'gasFee',
    'gasCoveredBySponsor',
    'storageCollateralized',
    'storageCoveredBySponsor',
    'storageReleased',
    'contractCreated',
    'stateRoot',
    'outcomeStatus',
    'logsBloom',
    'logs'
]

status_fields = [
    'networkId', 'chainId',
    'blockNumber', 'epochNumber',
    'bestHash',
    'pendingTxNumber',
    'latestState', 'latestCheckpoint', 'latestConfirmed'
]

account_fields = [
    'balance', 'stakingBalance',
    'nonce',
    'admin', 'codeHash',
    'collateralForStorage',
    'accumulatedInterestReturn'
]

estimate_fields = [
    'gasLimit',
    'gasUsed',
    'storageCollateralized'
]

def check_fields(to_check, fields):
    for f in fields:
        assert f in to_check

def test_getStatus():
    status = conflux.cfx.getStatus()
    check_fields(status, status_fields)
    assert status['networkId'] == 1
    assert status['chainId'] == 1
    assert type(status['blockNumber']) == int
    assert type(status['epochNumber']) == int
    assert type(status['pendingTxNumber']) == int
    assert type(status['latestCheckpoint']) == int
    assert type(status['latestConfirmed']) == int
    assert type(status['latestState']) == int
    assert type(status['bestHash']) == str

def test_gasPrice():
    price = conflux.cfx.gasPrice
    assert type(price) == int

def test_getNextNonce():
    nonce = conflux.cfx.getNextNonce(account)
    assert type(nonce) == int

def test_getBalance():
    balance = conflux.cfx.getBalance(account)
    assert type(balance) == int

def test_getStakingBalance():
    balance = conflux.cfx.getStakingBalance(account)
    assert type(balance) == int

def test_epochNumber():
    epoch_number = conflux.cfx.epochNumber()
    assert type(epoch_number) == int

def test_account():
    account_info = conflux.cfx.getAccount(account)
    check_fields(account_info, account_fields)
    assert type(account_info['balance']) == int
    assert type(account_info['nonce']) == int
    assert type(account_info['stakingBalance']) == int
    assert type(account_info['collateralForStorage']) == int
    assert type(account_info['accumulatedInterestReturn']) == int
    assert type(account_info['codeHash']) == str
    assert type(account_info['admin']) == str

def test_getBlockByHash():
    block = conflux.cfx.getBlockByHash(block_hash)
    check_fields(block, block_fields)
    assert type(block['adaptive']) == bool

def test_getBlockByEpochNumber():
    block = conflux.cfx.getBlockByEpochNumber(epoch_number)
    check_fields(block, block_fields)

def test_getTransactionByHash():
    tx = conflux.cfx.getTransactionByHash(tx_hash)
    check_fields(tx, tx_fields)

def test_getTransactionReceipt():
    receipt = conflux.cfx.getTransactionReceipt(tx_hash)
    check_fields(receipt, receipt_fields)

def test_getLogs():
    pass

def test_call():
    pass

def test_estimate():
    estimate = conflux.cfx.estimateGasAndCollateral(txinfo)
    check_fields(estimate, estimate_fields)

def test_sendRawTransaction():
    conflux.cfx.populate_transaction(txinfo)
    signed_tx = Account.sign_transaction(txinfo, private_key)
    tx_hash = conflux.cfx.sendRawTransaction(signed_tx.rawTransaction.hex())
    print(tx_hash)
