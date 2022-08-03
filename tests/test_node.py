from os import stat
import pytest

from conflux_web3 import Web3



# @pytest.fixture(scope="session")
# def w3(web3):
#     return web3

def test_local_node(node):
    secrets = node.secrets
    assert (len(secrets) > 0)


    