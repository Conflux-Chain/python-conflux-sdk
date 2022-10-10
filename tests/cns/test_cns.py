import pytest
from conflux_web3.dev import get_testnet_web3
from cns import CNS
from web3.exceptions import InvalidAddress
from conflux_web3 import Web3

def test_cns(w3, use_testnet):
    if use_testnet:
        ns = CNS.fromWeb3(w3)
        assert ns.address("jiuhua1.web3") == "cfxtest:aap8rzfhe7s7ju8ejrp2em4eamr3465y56r4cxb37e"

def test_cns_with_rpc(w3: Web3, use_testnet: bool):
    if use_testnet:
        balance = w3.cfx.get_balance("jiuhua1.web3")
        assert balance >= 0
    else:
        with pytest.raises(InvalidAddress):
            balance = w3.cfx.get_balance("jiuhua1.web3")
