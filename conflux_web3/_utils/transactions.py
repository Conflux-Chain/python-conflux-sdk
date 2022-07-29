
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
from web3.types import (
    TxParams
)

from conflux_web3.exceptions import NoWeb3Exception

if TYPE_CHECKING:
    from conflux_web3 import Web3


TRANSACTION_DEFAULTS = {
    "value": 0,
    "data": b"",
    "gasPrice": lambda w3, tx: w3.cfx.gas_price(tx),
    "chainId": lambda w3, tx: w3.cfx.chain_id,
    "epochHeight": lambda w3, tx: w3.cfx.epoch_number,
}



@curry
def fill_transaction_defaults(w3: "Web3", transaction: TxParams) -> TxParams:
    """
    if w3 is None, throw an exception
    """
    if w3 is None:
        raise NoWeb3Exception("A web3 object is required to fill transaction defaults, but no web3 object is detected")
        
    

    defaults = {}
    for key, default_getter in TRANSACTION_DEFAULTS.items():
        if key not in transaction:
            if (
                is_dynamic_fee_transaction
                and key == "gasPrice"
                or not is_dynamic_fee_transaction
                and key in DYNAMIC_FEE_TXN_PARAMS
            ):
                # do not set default max fees if legacy txn or
                # gas price if dynamic fee txn
                continue

            if callable(default_getter):
                if w3 is None:
                    raise ValueError(
                        f"You must specify a '{key}' value in the transaction"
                    )
                default_val = default_getter(w3, transaction)
            else:
                default_val = default_getter

            defaults[key] = default_val
    return merge(defaults, transaction)