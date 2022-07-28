from typing import Any, Callable


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

def conditional_func(real_func: Callable, condition: Callable[..., bool]):
    """decorate a function to optionally execute another one
    if condition:
        real_func
    else:
        original_func

    Args:
        real_func (Callable): function to be executed if condition
        condition (Callable[..., bool]): receives func arguments, returns a bool
    """
    def inner(func):
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                return real_func(*args, **kwargs)
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
