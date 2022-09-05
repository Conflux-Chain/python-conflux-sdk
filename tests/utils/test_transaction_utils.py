from audioop import add
import pytest
from conflux_web3 import Web3
from conflux_web3._utils.transactions import fill_transaction_defaults
from tests._test_helpers.type_check import TypeValidator

def test_fill_transaction_defaults(w3: Web3, address):
    """test inner util fill_transaction_defaults. 
    """
    w3.cfx.default_account = address
    # "from" field is required before using this util
    unfilled_tx = {
        "from": address,
        "to": w3.account.create().address
    }
    filled_tx = fill_transaction_defaults(w3, unfilled_tx)
    TypeValidator.validate_typed_dict(filled_tx, "TxDict")
