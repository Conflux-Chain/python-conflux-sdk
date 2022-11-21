from typing import TYPE_CHECKING
from conflux_web3 import Web3

def test_contract_type_hint(w3: Web3):
    # the following code will never be actually executed
    if TYPE_CHECKING:
        addr = w3.address.zero_address(w3.cfx.chain_id)
        # should be ConfluxContract
        erc20 = w3.cfx.contract(name="ERC20", with_deployment_info=True)
        erc20 = w3.cfx.contract(addr, name="ERC20", with_deployment_info=True)
        erc20 = w3.cfx.contract(addr, name="ERC20", with_deployment_info=False)
        erc20 = w3.cfx.contract(addr)
        
        # should be Type[ConfluxContract]
        erc20 = w3.cfx.contract(name="ERC20", with_deployment_info=False)
        erc20(addr)
        erc20 = w3.cfx.contract()
        erc20(addr)
        
        # should be ConfluxContract | Type[ConfluxContract]
        erc20 = w3.cfx.contract(name="ERC20")
