from cfx_account.account import LocalAccount
import pytest
from conflux_web3 import Web3
from conflux_web3.middleware.wallet import WalletMiddlewareFactory


def test_wallet_middleware_single_init(w3:Web3, account: LocalAccount):
    wallet = WalletMiddlewareFactory(w3.cfx.chain_id, account)
    w3.middleware_onion.add(wallet)
    tx = {
        'from': account.address,
        # 'nonce': w3.cfx.get_next_nonce(addr),
        # 'gas': 21000,
        'to': w3.cfx.account.create().address,
        'value': 10**9,
        # 'gasPrice': 10**9,
        # 'chainId': w3.cfx.chain_id,
        # 'storageLimit': 0,
        # 'epochHeight': status['epochNumber']
    }
    hash = w3.cfx.send_transaction(tx)
    assert hash
    w3.cfx.wait_for_transaction_receipt(hash)

def test_wallet_middleware_list_init(w3:Web3, account: LocalAccount):
    wallet = WalletMiddlewareFactory(w3.cfx.chain_id, [account])
    w3.middleware_onion.add(wallet)
    tx = {
        'from': account.address,
        # 'nonce': w3.cfx.get_next_nonce(addr),
        # 'gas': 21000,
        'to': w3.cfx.account.create().address,
        'value': 10**9,
        # 'gasPrice': 10**9,
        # 'chainId': w3.cfx.chain_id,
        # 'storageLimit': 0,
        # 'epochHeight': status['epochNumber']
    }
    hash = w3.cfx.send_transaction(tx)
    assert hash
    w3.cfx.wait_for_transaction_receipt(hash)
    

def test_wallet_middleware_adding(w3: Web3, account: LocalAccount):
    wallet = WalletMiddlewareFactory(w3.cfx.chain_id)
    wallet.add_accounts([account])
    w3.middleware_onion.add(wallet)
    tx = {
        'from': account.address,
        # 'nonce': w3.cfx.get_next_nonce(addr),
        # 'gas': 21000,
        'to': w3.cfx.account.create().address,
        'value': 10**9,
        # 'gasPrice': 10**9,
        # 'chainId': w3.cfx.chain_id,
        # 'storageLimit': 0,
        # 'epochHeight': status['epochNumber']
    }
    hash = w3.cfx.send_transaction(tx)
    assert hash
    w3.cfx.wait_for_transaction_receipt(hash)

def test_wallet_duplicate_adding_warning(w3: Web3):
    with pytest.warns(UserWarning):
        wallet = WalletMiddlewareFactory(w3.cfx.chain_id, random_account:=w3.account.create())
        wallet.add_account(random_account)
    