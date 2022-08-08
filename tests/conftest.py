from typing import Iterable
import os
import pytest
from tests._test_helpers.node import LocalNode, BaseNode, RemoteTestnetNode
from tests._test_helpers.ENV_SETTING import (
    PORT,
    LOCAL_HOST,
)

from cfx_account.account import LocalAccount
from conflux_web3 import (
    Web3
)


@pytest.fixture(scope="session")
def node() -> Iterable[BaseNode]:
    
    if os.environ.get("TESTNET_SECRET"):
        node = RemoteTestnetNode()
        yield node
    else:
        node = LocalNode()
        yield node
        node.exit()

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

@pytest.fixture
def address(w3: Web3, secret_key) -> str:
    addr = w3.account.from_key(secret_key).address
    return addr

@pytest.fixture
def account(w3: Web3, secret_key) -> LocalAccount:
    return w3.account.from_key(secret_key)
