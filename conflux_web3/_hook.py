# WARNING: 
# note that the hook won't effect already imported objects,
# so make sure this module is executed before any module of conflux_web3 or web3 is executed
# or the hook might not take effect
# else try directly importing the package to hook

from typing import (
    TYPE_CHECKING,
    Callable,
)
from cfx_utils.post_import_hook import (
    when_imported
)
from cfx_address import (
    Base32Address
)
from cfx_utils.exceptions import (
    InvalidEpochNumebrParam
)

if TYPE_CHECKING:
    from conflux_web3 import (
        Web3
    )
    from conflux_web3.types import (
        EpochNumberParam,
    )
    
    

def conditional_func(target_func: Callable, condition: Callable[..., bool]) -> Callable:
    """decorate a function to optionally execute another one
    if condition:
        target_func
    else:
        original_func

    Args:
        target_func (Callable): function to be executed if condition
        condition (Callable[..., bool]): receives func arguments, returns a bool
    """
    def inner(func) :
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                return target_func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return inner

def conditional_post_func(post_func: Callable, condition: Callable[..., bool]) -> Callable:
    """decorate a function to optionally execute post operation
    rtn = original_func
    if condition:
        post_func
    return rtn

    Args:
        post_func (Callable): function to be executed after original function if condition
        condition (Callable[..., bool]): receives func arguments, returns a bool
    """
    def inner(func) :
        def wrapper(*args, **kwargs):
            rtn = func(*args, **kwargs)
            if condition(*args, **kwargs):
                post_func(*args, **kwargs)
            else:
                pass
            return rtn
        return wrapper
    return inner

def cfx_web3_condition(*args, **kwargs) -> bool:
    """

    Returns:
        bool: returns if conflux_web3.Web3 type variable in arguments
    """
    from conflux_web3 import Web3
    for arg in list(args)+list(kwargs.values()):
        if isinstance(arg, Web3):
            return True
    return False

@when_imported("web3._utils.contracts")
def hook_encode_abi(mod):
    if mod.__name__ == "web3._utils.contracts":
        from conflux_web3._utils.contracts import cfx_encode_abi
        mod.encode_abi = conditional_func(
            cfx_encode_abi,
            cfx_web3_condition
        )(mod.encode_abi)

# used to hook web3.contract.parse_block_identifier
# hook is activated in conflux_web3._hook
def cfx_parse_block_identifier(
    w3: "Web3", block_identifier: "EpochNumberParam"
) -> "EpochNumberParam":
    if isinstance(block_identifier, int):
        return block_identifier
    elif block_identifier in ['earliest', 'latest_checkpoint', 'latest_finalized', 'latest_confirmed', 'latest_state', 'latest_mined']: # get_args("EpochLiteral")
        return block_identifier
    elif isinstance(block_identifier, bytes) or (
        isinstance(block_identifier, str) and block_identifier.startswith("0x")
    ):
        # r = 
        # assert r is not None
        return w3.cfx.get_block_by_hash(block_identifier)["epochNumber"] # type: ignore
    else:
        raise InvalidEpochNumebrParam

@when_imported("web3.contract")
def hook_parse_block_identifier(mod):
    # from conflux_web3.contract import cfx_parse_block_identifier
    if mod.__name__ == "web3.contract":
        mod.parse_block_identifier = conditional_func(
            cfx_parse_block_identifier,
            cfx_web3_condition
        )(mod.parse_block_identifier)
    
@when_imported("ethpm.package")
def hook_ethpm_package(mod):
    if mod.__name__ == "ethpm.package":
        from cfxpm.package import set_conflux_linkable_contract
        mod.Package.__init__ = conditional_post_func(
            set_conflux_linkable_contract,
            cfx_web3_condition
        )(mod.Package.__init__)

# hooked to is_none_or_zero_address in conflux_web3._hook
def is_none_or_base_32_zero_address(addr) -> bool:
    EMPTY_ADDR_HEX = "0x" + "00" * 20
    try:
        return (not addr) or (addr == EMPTY_ADDR_HEX) or (Base32Address.decode(addr)["hex_address"] == EMPTY_ADDR_HEX)
    except:
        return False

@when_imported("ens.utils")
def hook_is_none_or_zero_address(mod):
    if mod.__name__ == "ens.utils":
        mod.is_none_or_zero_address = is_none_or_base_32_zero_address

# we manually import ens.utils to hook is_none_or_zero_address because of insuccessful hook
import ens.utils
