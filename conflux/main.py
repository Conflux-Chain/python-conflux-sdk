from conflux._utils.rpc_abi import (
    RPC,
)
from web3.manager import (
    RequestManager as DefaultRequestManager,
)
from web3.providers import (
    BaseProvider,
)
from web3.providers.ipc import (
    IPCProvider,
)
from web3.providers.rpc import (
    HTTPProvider,
)
from web3.providers.websocket import (
    WebsocketProvider,
)
from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Sequence,
    TYPE_CHECKING
)
from web3._utils.module import (
    attach_modules,
)
from eth_abi.codec import (
    ABICodec,
)
from web3._utils.abi import (
    build_default_registry,
    build_strict_registry,
    map_abi_data,
)
from conflux.cfx import Cfx
from eth_utils import (
    to_wei,
    from_wei,
)
from eth_utils.address import (
    to_checksum_address
)
from eth_utils.conversions import (
    to_bytes
)
from web3._utils.contracts import (
    find_matching_fn_abi
)
from web3._utils.abi import (
    get_abi_output_types
)
from cfx_address import (
    Address
)
from web3 import (
    Web3,
)


def get_default_modules() -> Dict[str, Sequence[Any]]:
    return {
        "cfx": (Cfx,),
    }


class Conflux:
    # Providers
    HTTPProvider = HTTPProvider
    IPCProvider = IPCProvider
    WebsocketProvider = WebsocketProvider

    # Managers
    RequestManager = DefaultRequestManager

    # Currency Utility
    toDrip = staticmethod(to_wei)
    fromDrip = staticmethod(from_wei)

    cfx: Cfx

    def __init__(
            self,
            provider: Optional[BaseProvider] = None,
            middlewares: Optional[Sequence[Any]] = None,
            modules: Optional[Dict[str, Sequence[Any]]] = None,
    ) -> None:
        self.manager = self.RequestManager(self, provider, middlewares)

        self.codec = ABICodec(build_default_registry())

        if modules is None:
            modules = get_default_modules()

        attach_modules(self, modules)

        self._w3 = Web3(Web3.EthereumTesterProvider())

    @property
    def clientVersion(self) -> str:
        return self.manager.request_blocking(RPC.cfx_clientVersion, [])

    def contract(self, address, abi):
        hex_address = address
        if Address.has_network_prefix(address):
            hex_address = Address(address).eth_checksum_address

        return self._w3.eth.contract(address=hex_address, abi=abi)

    def call_contract_method(self, address, abi, method_name, *kargs):
        contract = self.contract(address, abi)
        tx = contract.functions[method_name](*kargs).buildTransaction({
            "gas": 21000,
            "gasPrice": 1,
        })
        call_result = self.cfx.call({
            "to": address,
            "data": tx['data']
        })
        fn_abi = find_matching_fn_abi(contract.abi, self._w3.codec, method_name, kargs)
        output_types = get_abi_output_types(fn_abi)
        decoded_result = self._w3.codec.decode_abi(output_types, to_bytes(hexstr=call_result))
        if len(output_types) == 1:
            return decoded_result[0]
        else:
            return decoded_result
