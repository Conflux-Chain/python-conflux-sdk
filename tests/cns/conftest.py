from typing import Union
import pytest
import os
from conflux_web3 import Web3
from cfx_account import LocalAccount

@pytest.fixture(scope="module")
def ens_name() -> Union[str, None]:
    ens_name = os.environ.get("ENS_ACCOUNT_NAME", None)
    return ens_name

@pytest.fixture(scope="module")
def ens_account(moduled_w3: Web3) -> Union[LocalAccount, None]:
    secret = os.environ.get("ENS_ACCOUNT_SECRET", None)
    if not secret:
        return None
    return moduled_w3.account.from_key(secret)
