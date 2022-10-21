import functools
from typing import (
    Any,
    Callable,
    NoReturn,
    Optional,
    TypeVar,
    Union,
    overload,
)
from typing_extensions import (
    ParamSpec,
)

from conflux_web3.exceptions import (
    DisabledException
)

T = TypeVar("T")
P = ParamSpec("P")


def temp_alter_module_variable(module: Any, varname: str, new_var: Any, condition: Callable[..., bool]):
    """temporarily alters module.varname to new_var before func is called, and recover the change afterwards

    Args:
        module (Any): the module to be temporarily changed
        varname (str): varname of the var to be changed
        new_var (Any): _description_
        condition (Callable[..., Boolean]): _description_
    """
    def inner(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            if condition(*args, **kwargs):
                cache = getattr(module, varname)
                module.__setattr__(varname, new_var)
                result = func(*args, **kwargs)
                module.__setattr__(varname, cache)
                return result
            return func(*args, **kwargs)
        return wrapper
    return inner

@overload
def use_instead(func: None=None, *, origin: str="This web3.eth api", substitute: Optional[str]=None) -> Callable[..., Callable[..., NoReturn]]: ...

@overload
def use_instead(func: Callable[..., Any], *, origin: str="This web3.eth api", substitute: Optional[str]=None) -> Callable[..., NoReturn]: ...

def use_instead(
    func: Optional[Callable[..., Any]]=None, *, origin: str="This web3.eth api", substitute: Optional[str]=None
) -> Union[Callable[..., Callable[..., NoReturn]], Callable[..., NoReturn]]:
    if func is None:
        return functools.partial(use_instead, origin=origin, substitute=substitute) # type: ignore
    
    @functools.wraps(func)
    def inner(*args: Any, **kwargs: Any) -> NoReturn:
        if substitute is None:
            raise DisabledException(f"{origin} is not valid in Conflux Network."
                            "Check https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#migrating-from-ethereum-json-rpc for more information")
        else:
            raise DisabledException(f"{origin} is not valid in Conflux Network, "
                            f"use {substitute} instead")
    return inner
