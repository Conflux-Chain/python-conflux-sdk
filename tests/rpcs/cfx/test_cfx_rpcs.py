import pytest
from hexbytes import HexBytes

from cfx_address import Base32Address
from conflux_web3 import Web3
from conflux_web3.types import (
    Drip,
)
from conflux_web3.contract.metadata import get_contract_metadata
from tests._test_helpers.type_check import TypeValidator

# Note that we only test if SDK works as expected, especially for request and result formatting.
# We don't test if RPC works as expected


def test_get_tx(moduled_w3: Web3, contract_address: Base32Address):
    """test get_transaction(_by_hash) and get_transaction_receipt
    """
    w3 = moduled_w3
    erc20_metadata = get_contract_metadata("ERC20")
    erc20 = w3.cfx.contract(address=contract_address, abi=erc20_metadata["abi"])

    tx_hash = erc20.functions.transfer(w3.account.create().address, 100).transact()
    transaction_data = w3.cfx.get_transaction(tx_hash)
    # transaction not added to chain
    TypeValidator.validate_tx_data(transaction_data)
    transaction_receipt = w3.cfx.wait_for_transaction_receipt(tx_hash)
    # already added
    TypeValidator.validate_tx_data(transaction_data)

    TypeValidator.validate_typed_dict(transaction_receipt, "TxReceipt")

def test_accounts(w3: Web3, use_testnet: bool):
    if use_testnet:
        assert True
        return
    
    local_node_accounts = w3.cfx.accounts
    assert len(local_node_accounts) == 10

# def test_get_logs(w3: Web3):
#     """see test_contract
#     """
#     pass


def test_get_confirmation_risk(w3: Web3, tx_hash: HexBytes):
    blockHash = w3.cfx.wait_for_transaction_receipt(tx_hash)['blockHash']
    risk = w3.cfx.get_confirmation_risk_by_hash(blockHash)
    assert risk < 1



def test_fee_history(moduled_w3: Web3):
    w3 = moduled_w3
    fee_history = w3.cfx.fee_history(5, "latest_state", [20,50])
    TypeValidator.validate_typed_dict(fee_history, "FeeHistory")


def test_max_priority_fee(moduled_w3: Web3):
    w3 = moduled_w3
    fee = w3.cfx.max_priority_fee
    assert isinstance(fee, Drip)
