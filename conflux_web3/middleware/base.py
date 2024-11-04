from typing import TYPE_CHECKING
from web3.middleware import Web3Middleware

if TYPE_CHECKING:
    from conflux_web3 import Web3
    

class ConfluxWeb3Middleware(Web3Middleware):
    _w3: "Web3"
