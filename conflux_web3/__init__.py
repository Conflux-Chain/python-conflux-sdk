# should be placed at the most front
import _web3_hook

from importlib.metadata import version

from conflux_web3.providers.rpc import HTTPProvider
from conflux_web3.main import Web3
from conflux_web3.dev import (
    get_local_web3,
    get_mainnet_web3,
    get_testnet_web3
)

__version__ = version("conflux_web3")

__all__ = [
    "Web3",
    "HTTPProvider",
    "get_local_web3",
    "get_mainnet_web3",
    "get_testnet_web3",
]
