from audioop import add
from threading import local
import time
import cfx_account
from hexbytes import HexBytes
import pytest

from cfx_account.account import LocalAccount
from conflux_web3 import Web3

from tests._test_helpers.type_check import  TypeValidator

class TestProperty:
    def test_get_status(self, w3: Web3):
        status = w3.cfx.get_status()
        TypeValidator.validate_typed_dict(status, "NodeStatus")

    def test_chain_id(self, w3: Web3):
        assert w3.cfx.chain_id > 0

    def test_gas_price(self, w3: Web3):
        gas_price = w3.cfx.gas_price
        assert gas_price >= 10**9
        assert isinstance(gas_price, int)

    def test_client_version(self, w3: Web3):
        assert w3.cfx.client_version

class TestBalance:
    def test_get_balance(self, w3: Web3, address):
        balance = w3.cfx.get_balance(address, w3.cfx.epoch_number-5)
        # the balance is supposed to be non-zero
        assert balance > 0
        # TODO: remove this part
        # if default account is set, 
        # default account is used as address default param
        # w3.cfx.default_account = address
        # default_balance = w3.cfx.get_balance()
        # assert default_balance == balance

    def test_get_balance_empty_param(self, w3: Web3):
        with pytest.raises(ValueError):
            w3.cfx.get_balance()

class TestNonce:
    def test_get_next_nonce(self, w3: Web3, address):
        nonce = w3.cfx.get_next_nonce(address, w3.cfx.epoch_number-5)
        assert nonce >= 0
        # if default account is set, 
        # default account is used as address default param
        w3.cfx.default_account = address
        default_nonce = w3.cfx.get_next_nonce()
        assert default_nonce == nonce

    def test_get_next_nonce_empty_param(self, w3: Web3):
        with pytest.raises(ValueError):
            w3.cfx.get_next_nonce()

@pytest.fixture(scope="module")
def txHash(moduled_w3: Web3, secret_key) -> HexBytes:
    w3 = moduled_w3
    status = w3.cfx.get_status()
    account = w3.account.from_key(secret_key)
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
    return w3.cfx.send_raw_transaction(rawTx)

def test_get_tx(w3: Web3, txHash: HexBytes):
    """test get_transaction(_by_hash) and get_transaction_receipt
    """
    transaction_data = w3.cfx.get_transaction(txHash)
    # transaction not added to chain
    TypeValidator.validate_typed_dict(transaction_data, "TxData")
    transaction_receipt = w3.cfx.wait_for_transaction_receipt(txHash)
    # already added
    TypeValidator.validate_typed_dict(transaction_data, "TxData")
    
    # TODO: check receipt's log format
    TypeValidator.validate_typed_dict(transaction_receipt, "TxReceipt")

def test_accounts(w3: Web3, use_remote: bool):
    if use_remote:
        assert True
        return
    
    local_node_accounts = w3.cfx.accounts
    assert len(local_node_accounts) == 10

def test_get_logs(w3: Web3):
    """see test_contract
    """
    pass

def test_get_confirmation_risk(w3: Web3, txHash):
    blockHash = w3.cfx.wait_for_transaction_receipt(txHash)['blockHash']
    risk = w3.cfx.get_confirmation_risk_by_hash(blockHash)
    assert risk < 1
