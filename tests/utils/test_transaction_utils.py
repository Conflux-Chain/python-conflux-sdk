from audioop import add
import pytest
from conflux_web3 import Web3
from conflux_web3._utils.transactions import fill_transaction_defaults
from cfx_address import Base32Address
from tests._test_helpers.type_check import TypeValidator
from conflux_web3._utils.transactions import tell_transaction_type
from cfx_address import Base32Address

def test_fill_transaction_defaults(w3: Web3, address:str):
    """test inner util fill_transaction_defaults. 
    """
    w3.cfx.default_account = address
    # "from" field is required before using this util
    unfilled_tx = {
        "from": Base32Address(address),
        "to": w3.account.create().address
    }
    filled_tx = fill_transaction_defaults(w3, unfilled_tx)
    TypeValidator.validate_typed_dict(filled_tx, "CIP1559TxDict")
    
    unfilled_tx = {
        "from": Base32Address(address),
        "to": w3.account.create().address,
        "gasPrice": 10**9
    }
    filled_tx = fill_transaction_defaults(w3, unfilled_tx)
    TypeValidator.validate_typed_dict(filled_tx, "LegacyTxDict")

def test_tell_transaction_type(address: str):

    assert tell_transaction_type({
        "from": Base32Address(address),
        "to": Base32Address(address)
    }) == 2
    
    assert tell_transaction_type({
        "from": Base32Address(address),
        "to": Base32Address(address),
        "gasPrice": 1
    }) == 0
    
    assert tell_transaction_type({
        "from": Base32Address(address),
        "to": Base32Address(address),
        "maxFeePerGas": 1,
    }) == 2
