from typing import Iterable
import os
import pytest
from tests._utils.node import LocalNode, BaseNode, RemoteTestnetNode
from tests._utils.ENV_SETTING import (
    PORT,
    LOCAL_HOST,
)

from conflux_web3 import (
    Web3
)

@pytest.fixture(scope="session")
def node() -> Iterable[BaseNode]:
    
    if os.environ.get("USE_TESTNET"):
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
def w3(node_url: str, node: LocalNode) -> Web3:
    """
    Returns:
        Web3: a web3 instance
    """
    provider = Web3.HTTPProvider(node_url)
    w3 = Web3(provider=provider)
    # assert w3.isConnected()
    return w3


@pytest.fixture(scope="session")
def secret_key(node: LocalNode) -> str:
    """
    Returns:
        str: secret key with enough balance
    """
    return node.secrets[0]

