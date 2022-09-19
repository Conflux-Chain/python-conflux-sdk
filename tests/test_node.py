from os import stat
import pytest

from conflux_web3 import Web3


def test_local_node(node, use_testnet):
    secrets = node.secrets
    if not use_testnet:
        assert (len(secrets) > 0)
