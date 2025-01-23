from typing import Optional, Sequence, Type
import time
import requests
from pydantic import BaseModel
from web3.providers.rpc import HTTPProvider as OriHTTPProvider
from web3.types import RPCEndpoint
from web3._utils.empty import (
    Empty,
)


REQUEST_RETRY_DISALLOWLIST = [
    "cfx_sendTransaction",
    "cfx_sendRawTransaction",
]

def check_if_retry_on_failure(
    method: RPCEndpoint,
    allowlist: Optional[Sequence[str]] = None,
    disallowlist: Optional[Sequence[str]] = None,
) -> bool:
    if allowlist != None and disallowlist != None:
        raise ValueError("allowlist and disallowlist cannot be used together")
    elif allowlist is None and disallowlist is None:
        disallowlist = REQUEST_RETRY_DISALLOWLIST
        
    if allowlist is not None:
        if method in allowlist or method.split("_")[0] in allowlist:
            return True
        else:
            return False
    if disallowlist is not None:
        if method in disallowlist or method.split("_")[0] in disallowlist:
            return False
        else:
            return True
    
    # Should never reach here
    raise ValueError("allowlist or disallowlist must be provided")


class ConfluxExceptionRetryConfiguration(BaseModel):
    errors: Sequence[Type[BaseException]]
    retries: int
    backoff_factor: float
    method_allowlist: Optional[Sequence[str]]
    method_disallowlist: Optional[Sequence[str]]

    def __init__(
        self,
        errors: Sequence[Type[BaseException]] = None,
        retries: int = 5,
        backoff_factor: float = 0.125,
        method_allowlist: Optional[Sequence[str]] = None,
        method_disallowlist: Optional[Sequence[str]] = None,
    ):
        super().__init__(
            errors=errors,
            retries=retries,
            backoff_factor=backoff_factor,
            method_allowlist=method_allowlist,
            method_disallowlist=method_disallowlist,
        )

class HTTPProvider(OriHTTPProvider):
    @property
    def exception_retry_configuration(self) -> ConfluxExceptionRetryConfiguration:
        if isinstance(self._exception_retry_configuration, Empty):
            self._exception_retry_configuration = ConfluxExceptionRetryConfiguration(
                errors=(
                    ConnectionError,
                    requests.HTTPError,
                    requests.Timeout,
                )
            )
        return self._exception_retry_configuration
    
    def _make_request(self, method: RPCEndpoint, request_data: bytes) -> bytes:
        if (
            self.exception_retry_configuration is not None
            and check_if_retry_on_failure(
                method, self.exception_retry_configuration.method_allowlist
            )
        ):
            for i in range(self.exception_retry_configuration.retries):
                try:
                    return self._request_session_manager.make_post_request(
                        self.endpoint_uri, request_data, **self.get_request_kwargs()
                    )
                except tuple(self.exception_retry_configuration.errors) as e:
                    if i < self.exception_retry_configuration.retries - 1:
                        time.sleep(
                            self.exception_retry_configuration.backoff_factor * 2**i
                        )
                        continue
                    else:
                        raise e
            return None
        else:
            return self._request_session_manager.make_post_request(
                self.endpoint_uri, request_data, **self.get_request_kwargs()
            )
    
