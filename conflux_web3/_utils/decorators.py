import functools
from typing import (
    Any,
    Callable
)

from conflux_web3.exceptions import (
    DisabledException
)


def temp_alter_module_variable(module: Any, varname: str, new_var: Any, condition: Callable[..., bool]):
    """temporarily alters module.varname to new_var before func is called, and recover the change afterwards

    Args:
        module (Any): the module to be temporarily changed
        varname (str): varname of the var to be changed
        new_var (Any): _description_
        condition (Callable[..., Boolean]): _description_
    """
    def inner(func):
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                cache = getattr(module, varname)
                module.__setattr__(varname, new_var)
                result = func(*args, **kwargs)
                module.__setattr__(varname, cache)
                return result
            return func(*args, **kwargs)
        return wrapper
    return inner

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

def use_instead(func=None, *, origin="This web3.eth api", substitute=None):
    if func is None:
        return functools.partial(use_instead, substitute=substitute)
    
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if substitute is None:
            raise DisabledException(f"{origin} is not valid in Conflux Network."
                            "Check https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#migrating-from-ethereum-json-rpc for more information")
        else:
            raise DisabledException(f"{origin} is not valid in Conflux Network, "
                            f"use {substitute} instead")
    return inner
