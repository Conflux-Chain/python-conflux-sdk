
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

from cfx_utils.token_unit import (
    Drip
)
from conflux_web3.exceptions import (
    NoWeb3Exception
)
from conflux_web3.types import TxParam

if TYPE_CHECKING:
    from conflux_web3 import Web3


TRANSACTION_DEFAULTS = {
    "value": 0,
    "data": b"",
    "nonce": lambda w3, tx, estimate=None: w3.cfx.get_next_nonce(tx['from']),
    "gas": lambda w3, tx, estimate=None: estimate["gasLimit"],
    "storageLimit": lambda w3, tx, estimate=None: estimate["storageCollateralized"],
    # convert to int value
    "gasPrice": lambda w3, tx, estimate=None: w3.cfx.gas_price.to(Drip).value,
    "chainId": lambda w3, tx, estimate=None: w3.cfx.chain_id,
    "epochHeight": lambda w3, tx, estimate=None: w3.cfx.epoch_number,
}


@curry
def fill_transaction_defaults(w3: "Web3", transaction: TxParam) -> TxParam:
    """
    Fill the necessary fields to "send" a transaction
    Before this function is invoked, ensure 'from' field is filled
    """
    if not w3:
        raise NoWeb3Exception("A web3 object is required to fill transaction defaults, but no web3 object is passed")
    if (not transaction.get("from")) and (transaction.get("nonce", None) is None):
        raise ValueError("Transaction's 'from' field is required to fill nonce field")
    
    for key, default_getter in TRANSACTION_DEFAULTS.items():
        estimate = None
        if key not in transaction:
            if callable(default_getter):
                if not estimate:
                    if key == "gas" or key == "storageLimit":
                        estimate = w3.cfx.estimate_gas_and_collateral(transaction)
                default_val = default_getter(w3, transaction, estimate)
                
            else:
                default_val = default_getter

            transaction.setdefault(key, default_val) # type: ignore
    return transaction
