from audioop import add
from threading import local
import cfx_account
import pytest

from cfx_account.account import LocalAccount
from conflux_web3 import Web3

from tests._test_helpers.type_check import  TypeValidator


def test_get_status(w3: Web3):
    status = w3.cfx.get_status()
    TypeValidator.validate_status(status)


def test_chain_id(w3: Web3):
    assert w3.cfx.chain_id > 0


def test_gas_price(w3: Web3):
    gas_price = w3.cfx.gas_price
    assert gas_price >= 10**9
    assert isinstance(gas_price, int)
    
def test_get_balance(w3: Web3, address):
    balance = w3.cfx.get_balance(address)
    # the balance is supposed to be non-zero
    assert balance > 0
    # if default account is set, 
    # default account is used as address default param
    w3.cfx.default_account = address
    default_balance = w3.cfx.get_balance()
    assert default_balance == balance

def test_get_balance_empty_param(w3: Web3):
    with pytest.raises(ValueError):
        w3.cfx.get_balance()
    
    
def test_get_next_nonce(w3: Web3, address):
    nonce = w3.cfx.get_next_nonce(address)
    assert nonce >= 0
    # if default account is set, 
    # default account is used as address default param
    w3.cfx.default_account = address
    default_nonce = w3.cfx.get_next_nonce()
    assert default_nonce == nonce

def test_get_next_nonce_empty_param(w3: Web3):
    with pytest.raises(ValueError):
        w3.cfx.get_next_nonce()

def test_get_tx_reciept(w3: Web3, account: LocalAccount):
    status = w3.cfx.get_status()
    
    addr = account.address
    
    tx = {
        'from': addr,
        'nonce': w3.cfx.get_next_nonce(addr),
        'gas': 21000,
        'to': "cfxtest:aamd4myx7f3en2yu95xye7zb78gws09gj2ykmv9p58",
        'value': 100,
        'gasPrice': 10**9,
        'chainId': w3.cfx.chain_id,
        'storageLimit': 0,
        'epochHeight': status['epochNumber']
    }
    signed = account.sign_transaction(tx)
    rawTx = signed.rawTransaction
    r = w3.cfx.send_raw_transaction(rawTx)
    w3.cfx.wait_for_transaction_receipt(r)
    transaction_receipt = w3.cfx.get_transaction_receipt(r)
    assert transaction_receipt
