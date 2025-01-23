import pytest
from unittest.mock import (
    patch,
)
from conflux_web3 import Web3
from conflux_web3._utils.rpc_abi import (
    RPC
)
from requests.exceptions import (
    Timeout,
)
from conflux_web3.providers.rpc import check_if_retry_on_failure

@pytest.fixture
def w3() -> Web3:
    return Web3(Web3.HTTPProvider())


def test_default_check_if_retry_on_failure():
    assert check_if_retry_on_failure(RPC.cfx_sendRawTransaction) == False
    assert check_if_retry_on_failure(RPC.cfx_getBalance) == True


def test_check_if_retry_on_failure_with_allowlist():
    assert check_if_retry_on_failure(RPC.cfx_sendRawTransaction, allowlist=["cfx_sendRawTransaction"]) == True
    assert check_if_retry_on_failure(RPC.cfx_sendRawTransaction, allowlist=["cfx_sendTransaction"]) == False
    
def test_check_if_retry_on_failure_with_disallowlist():
    assert check_if_retry_on_failure(RPC.cfx_sendRawTransaction, disallowlist=["cfx_sendRawTransaction"]) == False
    assert check_if_retry_on_failure(RPC.cfx_sendRawTransaction, disallowlist=["cfx_sendTransaction"]) == True

def test_default_exception_retry(w3: Web3):
    with patch(
        "web3.providers.rpc.rpc.HTTPSessionManager.make_post_request"
    ) as make_post_request_mock:
        make_post_request_mock.side_effect = Timeout

        with pytest.raises(Timeout):
            w3.cfx.get_status()
        assert make_post_request_mock.call_count == 5  # default retry count is 5

def test_default_exception_no_retry(w3: Web3):
    with patch(
        "web3.providers.rpc.rpc.HTTPSessionManager.make_post_request"
    ) as make_post_request_mock:
        make_post_request_mock.side_effect = Timeout

        with pytest.raises(Timeout):
            w3.cfx.send_raw_transaction("0x")
        assert make_post_request_mock.call_count == 1  # only once