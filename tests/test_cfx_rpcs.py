from threading import local
import cfx_account
import pytest
from conflux_web3 import Web3
from tests._utils.type_check import Hash32Str

status_fields = {
    "bestHash": Hash32Str,
    "chainId": int,
    "networkId": int,
    "blockNumber": int,
    "epochNumber": int,
    "latestCheckpoint": int,
    "latestConfirmed": int,
    "latestState": int,
    "latestFinalized": int,
    "ethereumSpaceChainId": int,
    "pendingTxNumber": int,
}

def test_get_status(w3: Web3):
    status = w3.cfx.get_status()
    for field, field_type in status_fields.items():
        assert field in status
        assert isinstance(status[field], field_type)


# @pytest.fixture
def test_chain_id(w3: Web3):
    assert w3.cfx.chain_id > 0

# def test_chain_id(chain_id):
#     assert chain_id > 0

@pytest.fixture
def address(w3: Web3, secret_key) -> str:
    chain_id = w3.cfx.chain_id
    local_account = w3.account.from_key(secret_key, chain_id)
    return local_account.address

def test_gas_price(w3: Web3):
    gas_price = w3.cfx.gas_price
    assert gas_price >= 10**9
    assert isinstance(gas_price, int)
    
def test_get_balance(w3: Web3, address):
    balance = w3.cfx.get_balance(address)
    # the balance is supposed to be non-zero
    assert balance > 0
    
def test_get_next_nonce(w3: Web3, address):
    nonce = w3.cfx.get_next_nonce(address)
    assert nonce >= 0
    