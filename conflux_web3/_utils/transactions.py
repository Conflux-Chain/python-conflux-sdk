
from inspect import Parameter
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    cast,
)
from eth_utils.toolz import (
    # assoc,
    curry,  # type: ignore
    merge,  # type: ignore
)

from conflux_web3.exceptions import (
    NoWeb3Exception
)
from conflux_web3.types import TxParam

if TYPE_CHECKING:
    from conflux_web3 import Web3

# TODO: don't estimate twice or fas and storageLimit
TRANSACTION_DEFAULTS = {
    "value": 0,
    "data": b"",
    "nonce": lambda w3, tx: w3.cfx.get_next_nonce(tx['from']),
    "gas": lambda w3, tx: w3.cfx.estimate_gas_and_collateral(tx)["gasLimit"],
    "storageLimit": lambda w3, tx: w3.cfx.estimate_gas_and_collateral(tx)["storageCollateralized"],
    "gasPrice": lambda w3, tx: w3.cfx.gas_price,
    "chainId": lambda w3, tx: w3.cfx.chain_id,
    "epochHeight": lambda w3, tx: w3.cfx.epoch_number,
}



@curry
def fill_formal_transaction_defaults(w3: "Web3", transaction: TxParam) -> TxParam:
    """
    Fill the necessary fields to "send" a transaction
    Before this function is invoked, ensure 'from' field is filled
    """
    if not w3:
        raise NoWeb3Exception("A web3 object is required to fill transaction defaults, but no web3 object is passed")
    if (not transaction.get("from")) and (transaction.get("nonce", None) is None):
        raise ValueError("Transaction's 'from' field is required to fill nonce field")
    
    for key, default_getter in TRANSACTION_DEFAULTS.items():
        if key not in transaction:
            if callable(default_getter):
                default_val = default_getter(w3, transaction)
            else:
                default_val = default_getter

            transaction.setdefault(key, default_val) # type: ignore
    return transaction
