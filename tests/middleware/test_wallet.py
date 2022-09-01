import pytest
from cfx_account.account import LocalAccount
from cfx_account import (
    Account
)
from conflux_web3 import Web3
from conflux_web3.middleware.wallet import (
    Wallet,
    construct_sign_and_send_raw_middleware
)


def test_wallet_middleware_single_init(w3:Web3, account: LocalAccount):
    wallet = construct_sign_and_send_raw_middleware(account, w3.cfx.chain_id)
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

def test_no_chain_id_wallet_middleware_single_init(w3:Web3, account: LocalAccount):
    wallet = construct_sign_and_send_raw_middleware(account)
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
    wallet = Wallet([account], w3.cfx.chain_id)
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
    wallet = Wallet(forced_chain_id=w3.cfx.chain_id)
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

def test_default_wallet_middleware_adding(w3: Web3, account: LocalAccount):
    w3.wallet.add_accounts([account])
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
        wallet = Wallet(random_account:=w3.account.create(), w3.cfx.chain_id)
        wallet.add_account(random_account)

def test_wallet_chain_id_compatibility(w3: Web3):
    chain_id = w3.cfx.chain_id
    wallet = Wallet(forced_chain_id=chain_id+1)
    
    # compatible account with no chain id
    wallet.add_account(
        Account.create()
    )
    
    # incompatible account with incompatible chain id
    with pytest.raises(ValueError):
        wallet.add_account(
            w3.account.create()
        )
    
    wallet.forced_chain_id = chain_id
    wallet.add_account(
        w3.account.create()
    )

def test_wallet_accounts_property():
    wallet = Wallet()
    wallet.add_account(
        account := Account.create()
    )
    assert account.address in wallet.accounts
    
def test_wallet_operators():
    wallet = Wallet()
    wallet.add_account(
        account := Account.create()
    )
    # __contains__
    assert account.address in wallet
    # __getitem__
    assert wallet[account.address]
