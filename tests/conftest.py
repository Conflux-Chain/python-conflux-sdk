from typing import Iterable, Sequence
import os
import pytest
from tests._test_helpers.node import LocalNode, BaseNode, RemoteTestnetNode
from tests._test_helpers.ENV_SETTING import (
    PORT,
    LOCAL_HOST,
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
def use_remote() -> bool:
    return bool(os.environ.get("TESTNET_SECRET"))

@pytest.fixture(scope="session")
def node(use_remote) -> Iterable[BaseNode]:
    if use_remote:
        node = RemoteTestnetNode()
        yield node
    else:
        node = LocalNode()
        yield node
        # node.exit()

@pytest.fixture(scope="session")
def node_url(node):
    return node.url

@pytest.fixture(scope="session")
def secret_key(node: LocalNode) -> str:
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
    # assert w3.isConnected()
    return w3

@pytest.fixture(scope="module")
def moduled_w3(node_url: str, node: LocalNode, secret_key) -> Web3:
    """
    a web3 instance for the convenience to create module shared objects
    e.g. a transaction or a contract which is required for the module
    NOTE: DON'T CHANGE PROPERTY OF THIS W3
    """
    account = Account.from_key(secret_key, )
    provider = Web3.HTTPProvider(node_url)
    w3 = Web3(provider=provider)
    # assert w3.isConnected()
    w3.cfx.default_account = account.get_base32_address(w3.cfx.chain_id)
    w3.middleware_onion.add(
        Wallet(account)
    )
    return w3

@pytest.fixture(scope="session")
def address(node_url, secret_key) -> str:
    chain_id = Web3(Web3.HTTPProvider(node_url)).cfx.chain_id
    addr = Account.from_key(secret_key, chain_id).address
    return addr

@pytest.fixture
def account(w3: Web3, secret_key) -> LocalAccount:
    """external_account, not supported by node
    """
    return w3.account.from_key(secret_key)


@pytest.fixture
def embedded_accounts(w3: Web3, use_remote: bool) -> Sequence[Base32Address]:
    if use_remote:
        return []
    return w3.cfx.accounts