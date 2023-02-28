from uuid import uuid4
import sys
import pytest
from conflux_web3 import Web3
from cns import CNS
from cfx_account import LocalAccount
from conflux_web3.exceptions import (
    NameServiceNotSet
)

@pytest.fixture
def to_test_cns_write_api(use_testnet: bool) -> bool:
    # currently we only support cns write api on testnet
    # so we only do tests on python3.8 to avoid nonce problems
    return sys.version_info.minor == 8 and use_testnet

def test_cns(w3: Web3, use_testnet, ens_name, ens_account):
    if use_testnet and ens_name:
        ns = CNS.fromWeb3(w3)
        assert ns.address(ens_name)
        if ens_account:
            assert ns.address(ens_name) == ens_account.address

def test_cns_from_address(use_testnet: bool, ens_name: str, ens_account: LocalAccount):
    if use_testnet:
        provider = Web3.HTTPProvider("https://test.confluxrpc.com")
        cns = CNS(provider, "cfxtest:acemru7fu1u8brtyn3hrtae17kbcd4pd9u2m761bta")
        assert cns.address(ens_name) == ens_account.address
        w3 = Web3(provider, cns=cns)
        assert w3.cns.address(ens_name) == ens_account.address

    

def test_cns_with_rpc(w3: Web3, use_testnet: bool, ens_name):
    if use_testnet:
        balance = w3.cfx.get_balance(ens_name)
        assert balance >= 0
    else:
        with pytest.raises(NameServiceNotSet):
            balance = w3.cfx.get_balance("hello45678oiuytrrtyuiytredcv.web3")
            
def test_cns_usage_as_contract_param(w3: Web3, to_test_cns_write_api, account, ens_name):
    if to_test_cns_write_api:
        w3.cfx.default_account = account
        erc20 = w3.cfx.contract(name="ERC20", with_deployment_info=False)
        addr = erc20.constructor("Token", "T", 100).transact().executed()["contractCreated"]
        assert addr is not None
        erc20 = erc20(address=addr)
        assert erc20.functions.transfer(ens_name, 100).transact().executed()
        assert erc20.caller.balanceOf(ens_name) == 100 

def test_cns_as_sender(w3: Web3, to_test_cns_write_api, ens_account, ens_name):
    if to_test_cns_write_api:
        w3.wallet.add_account(ens_account)
        w3.cfx.send_transaction({
            "to": w3.account.create().address,
            "value": 100,
            "from": ens_name
        }).executed()

def test_cns_as_contract_address(w3: Web3, to_test_cns_write_api):
    if to_test_cns_write_api:
        faucet = w3.cfx.contract("faucet.web3", name="Faucet", with_deployment_info=False)
        assert faucet.address == "cfxtest:acejjfa80vj06j2jgtz9pngkv423fhkuxj786kjr61"
        account = w3.cfx.account.create()
        w3.cfx.default_account = account
        faucet.functions.claimCfx().transact().executed()

def test_cns_as_default_account(w3: Web3, use_testnet, ens_name, ens_account):
    if use_testnet:
        w3.cfx.default_account = ens_name
        assert w3.cfx.default_account == ens_account.address

def test_cns_owner(w3: Web3, use_testnet, ens_name):
    if use_testnet:
        assert w3.ens.owner(ens_name)

# def test_setup_owner(w3: Web3, account):
#     w3.cns.allow_unstable_api = True
#     w3.cfx.default_account = account
#     w3.cns.setup_owner("test.web3", wrapped=True)

def test_setup_address(w3: Web3, to_test_cns_write_api, ens_account):
    if to_test_cns_write_api:
        w3.cns.allow_unstable_api = True
        w3.cfx.default_account = ens_account
        random_address = w3.account.create().address
        
        assert w3.cns.setup_address("test.web3", random_address, wrapped=True).executed()

        # test setup subdomain address
        random_subdomain = uuid4()
        assert w3.cns.setup_address(f"{random_subdomain}.test.web3", random_address, wrapped=True).executed()
        assert w3.cns.address(f"{random_subdomain}.test.web3") == random_address
        

def test_cns_wallet(w3: Web3, use_testnet):
    if use_testnet:
        assert w3.wallet is w3.cns.w3.wallet

def test_cns_default_account(w3: Web3, use_testnet, account):
    if use_testnet:
        w3.cfx.default_account = account
        assert w3.cfx.default_account == w3.ens.w3.cfx.default_account
