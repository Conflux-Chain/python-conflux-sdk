# should be placed at the most front
import _web3_hook

import pkg_resources

from conflux_web3.main import Web3
from conflux_web3.dev import (
    get_local_web3,
    get_mainnet_web3,
    get_testnet_web3
)
HTTPProvider = Web3.HTTPProvider

__version__ = pkg_resources.get_distribution("conflux_web3").version

__all__ = [
    "Web3",
    "HTTPProvider",
    "get_local_web3",
    "get_mainnet_web3",
    "get_testnet_web3",
]
