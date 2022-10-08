from typing import Iterable, Sequence, Union
import os
import pytest
from tests._test_helpers.node import (
    LocalNode, BaseNode, RemoteTestnetNode, LocalTestnetNode
)

from cfx_account.account import LocalAccount
from cfx_account import Account
from conflux_web3 import (
    Web3
)
from conflux_web3.types import (
    Base32Address
)
from conflux_web3.middleware import (
    Wallet
)

@pytest.fixture(scope="session")
def use_testnet() -> bool:
    return bool(os.environ.get("TESTNET_SECRET")) or bool(os.environ.get("USE_TESTNET"))

@pytest.fixture(scope="session")
def node(use_testnet) -> Iterable[BaseNode]:
    if use_testnet:
        node = RemoteTestnetNode() # connection error might occur if using public RPC
        # node = LocalTestnetNode() 
        yield node
        # node.exit()
    else:
        node = LocalNode()
        yield node
        # node.exit()

@pytest.fixture(scope="session")
def node_url(node):
    return node.url

@pytest.fixture(scope="session")
def secret_key(node: LocalNode) -> Union[str, None]:
    """
    Returns:
        str: secret key with enough balance
    """
    return node.secrets[0]

# no scope here
@pytest.fixture
def w3(node_url: str, node: LocalNode) -> Web3:
    """
    Returns:
        Web3: a web3 instance
    """
    provider = Web3.HTTPProvider(node_url)
    w3 = Web3(provider=provider)
    return w3

@pytest.fixture(scope="session")
def account(node_url: str, secret_key) -> LocalAccount:
    """external_account, not supported by node
    """
    provider = Web3.HTTPProvider(node_url)
    w3 = Web3(provider=provider)
    acct = w3.account.from_key(secret_key)
    if w3.cfx.get_balance(acct.address) != 0:
        return w3.account.from_key(secret_key)
    elif w3.cfx.chain_id == 1:
        w3.cfx.default_account = acct
        faucet = w3.cfx.contract(name="Faucet")
        faucet.functions.claimCfx().transact().executed()
        return acct
    else:
        raise Exception("Unexpected exception: not local nor testnet node and no environment secret key is set")

@pytest.fixture(scope="module")
def moduled_w3(node_url: str, node: LocalNode, account) -> Web3:
    """
    a web3 instance for the convenience to create module shared objects
    e.g. a transaction or a contract which is required for the module
    NOTE: DON'T CHANGE PROPERTY OF THIS W3
    """
    # account = Account.from_key(secret_key, )
    provider = Web3.HTTPProvider(node_url)
    w3 = Web3(provider=provider)
    w3.cfx.default_account = account
    return w3

@pytest.fixture(scope="session")
def address(node_url, secret_key) -> str:
    chain_id = Web3(Web3.HTTPProvider(node_url)).cfx.chain_id
    addr = Account.from_key(secret_key, chain_id).address
    return addr

@pytest.fixture
def embedded_accounts(w3: Web3, use_testnet: bool) -> Sequence[Base32Address]:
    if use_testnet:
        return []
    return w3.cfx.accounts
