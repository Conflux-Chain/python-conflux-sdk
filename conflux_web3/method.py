from typing import (
    Generic,
    Optional,
    Sequence,
    Callable,
)
from web3.method import (
    Method,
    Munger,
    TFunc
)
from web3.types import (
    RPCEndpoint,
    TReturn
)
from conflux_web3._utils.method_formatters import (
    cfx_request_formatters,
    cfx_result_formatters,
)


class ConfluxMethod(Method, Generic[TFunc]):
    def __init__(
        self,
        json_rpc_method: Optional[RPCEndpoint] = None,
        mungers: Optional[Sequence[Munger]] = None,
        request_formatters: Optional[Callable[..., TReturn]] = None,
        result_formatters: Optional[Callable[..., TReturn]] = None,
        null_result_formatters: Optional[Callable[..., TReturn]] = None,
        method_choice_depends_on_args: Optional[Callable[..., RPCEndpoint]] = None,
        is_property: bool = False,
    ):
        request_formatters = request_formatters or cfx_request_formatters  # type: ignore
        result_formatters = result_formatters or cfx_result_formatters # type: ignore
        Method.__init__(self, 
                        json_rpc_method, 
                        mungers, 
                        request_formatters, 
                        result_formatters, 
                        null_result_formatters,
                        method_choice_depends_on_args,
                        is_property
                        )