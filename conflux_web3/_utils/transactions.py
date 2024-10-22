
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    cast,
)
from hexbytes import HexBytes
from eth_utils.toolz import (
    # assoc,
    curry,  # type: ignore
    merge,  # type: ignore
)

from cfx_utils.token_unit import (
    Drip
)
from cfx_utils.types import (
    CIP1559TxDict
)
from conflux_web3.exceptions import (
    NoWeb3Exception
)
from conflux_web3.types import (
    TxParam,
)
from conflux_web3._utils.cns import (
    resolve_if_cns_name,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3


LEGACY_TRANSACTION_DEFAULTS = {
    "value": 0,
    "data": b"",
    "nonce": lambda w3, tx, estimate=None: w3.cfx.get_next_nonce(tx['from']), # type: ignore
    "gas": lambda w3, tx, estimate=None: estimate["gasLimit"], # type: ignore
    "storageLimit": lambda w3, tx, estimate=None: estimate["storageCollateralized"], # type: ignore
    # convert to int value
    "gasPrice": lambda w3, tx, estimate=None: w3.cfx.gas_price.to(Drip).value, # type: ignore
    "chainId": lambda w3, tx, estimate=None: w3.cfx.chain_id, # type: ignore
    "epochHeight": lambda w3, tx, estimate=None: w3.cfx.epoch_number, # type: ignore
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
    if "from" in transaction:
        transaction['from'] = resolve_if_cns_name(w3, transaction['from'])
    
    transaction_type = tell_transaction_type(transaction)
    if transaction_type == 0:
        return set_legacy_transaction_defaults(w3, transaction)
    elif transaction_type == 2:
        return set_cip1559_transaction_defaults(w3, transaction)
    else:
        raise ValueError(f"Transaction type not supported: {transaction_type}")

def tell_transaction_type(transaction: TxParam) -> int:
    if "type" in transaction:
        return int(HexBytes(transaction["type"]))
    if "gasPrice" in transaction:
        return 0
    if "maxFeePerGas" in transaction or "maxPriorityFeePerGas" in transaction:
        return 2
    return 2

def set_legacy_transaction_defaults(w3: "Web3", transaction: TxParam) -> TxParam:
    estimate = None
    if "value" not in transaction:
        transaction["value"] = 0
    if "data" not in transaction:
        transaction["data"] = b""
    if "nonce" not in transaction:
        transaction["nonce"] = w3.cfx.get_next_nonce(transaction["from"])
    if "gas" not in transaction:
        estimate = w3.cfx.estimate_gas_and_collateral(transaction)
        transaction["gas"] = estimate["gasLimit"]
    if "storageLimit" not in transaction:
        if not estimate:
            estimate = w3.cfx.estimate_gas_and_collateral(transaction)
        transaction["storageLimit"] = estimate["storageCollateralized"]
    if "gasPrice" not in transaction:
        transaction["gasPrice"] = w3.cfx.gas_price.to(Drip).value
    if "chainId" not in transaction:
        transaction["chainId"] = w3.cfx.chain_id
    if "epochHeight" not in transaction:
        transaction["epochHeight"] = w3.cfx.epoch_number
    transaction["type"] = 0
    return transaction

def set_cip1559_transaction_defaults(w3: "Web3", transaction: CIP1559TxDict) -> TxParam:
    estimate = None
    if "value" not in transaction:
        transaction["value"] = 0
    if "data" not in transaction:
        transaction["data"] = b""
    if "nonce" not in transaction:
        transaction["nonce"] = w3.cfx.get_next_nonce(transaction["from"])
    if "gas" not in transaction:
        estimate = w3.cfx.estimate_gas_and_collateral(transaction)
        transaction["gas"] = estimate["gasLimit"]
    if "storageLimit" not in transaction:
        if not estimate:
            estimate = w3.cfx.estimate_gas_and_collateral(transaction)
        transaction["storageLimit"] = estimate["storageCollateralized"]
    if "maxPriorityFeePerGas" not in transaction:
        transaction["maxPriorityFeePerGas"] = w3.cfx.max_priority_fee.to(Drip).value
    if "maxFeePerGas" not in transaction:
        base_fee = w3.cfx.get_block("latest_state")["baseFeePerGas"] * 2
        transaction["maxFeePerGas"] = (base_fee + Drip(transaction["maxPriorityFeePerGas"])).to(Drip).value
    if "chainId" not in transaction:
        transaction["chainId"] = w3.cfx.chain_id
    if "epochHeight" not in transaction:
        transaction["epochHeight"] = w3.cfx.epoch_number
    transaction["type"] = 2
    return transaction