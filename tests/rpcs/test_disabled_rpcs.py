import pytest
from conflux_web3 import Web3
from conflux_web3._utils.disabled_eth_apis import disabled_list
from conflux_web3.exceptions import DisabledException

def test_disabled_rpcs(w3: Web3):
    for method in disabled_list:
        with pytest.raises(DisabledException):
            getattr(w3.cfx, method)()
