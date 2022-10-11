import pytest
from conflux_web3.dev import get_testnet_web3
from cns import CNS
from web3.exceptions import InvalidAddress
from conflux_web3 import Web3

def test_cns(w3: Web3, use_testnet, ens_name, ens_account):

    if use_testnet and ens_name:
        ns = CNS.fromWeb3(w3)
        assert ns.address(ens_name)
        if ens_account:
            assert ns.address(ens_name) == ens_account.address

def test_cns_with_rpc(w3: Web3, use_testnet: bool, ens_name):
    if use_testnet:
        balance = w3.cfx.get_balance(ens_name)
        assert balance >= 0
    else:
        with pytest.raises(InvalidAddress):
            balance = w3.cfx.get_balance(ens_name)
            
def test_cns_usage_as_contract_param(w3: Web3, use_testnet, account, ens_name):
    if use_testnet:
        w3.cfx.default_account = account
        erc20 = w3.cfx.contract(name="ERC20")
        addr = erc20.constructor("Token", "T", 100).transact().executed()["contractCreated"]
        assert addr is not None
        erc20 = erc20(address=addr)
        assert erc20.functions.transfer(ens_name, 100).transact().executed()
        assert erc20.caller.balanceOf(ens_name) == 100 

def test_cns_as_sender(w3: Web3, ens_account, ens_name):
    if ens_account:
        w3.wallet.add_account(ens_account)
        w3.cfx.send_transaction({
            "to": w3.account.create().address,
            "value": 100,
            "from": ens_name
        }).executed()

def test_cns_as_contract_address(w3: Web3, use_testnet):
    if use_testnet:
        faucet = w3.cfx.contract("faucet.web3", name="faucet", with_deployment_info=False)
        assert faucet.address == "cfxtest:acejjfa80vj06j2jgtz9pngkv423fhkuxj786kjr61"
        account = w3.cfx.account.create()
        w3.cfx.default_account = account
        faucet.functions.claimCfx().transact().executed()

def test_cns_as_default_account(w3: Web3, ens_name, ens_account):
    if ens_name:
        w3.cfx.default_account = ens_name
        assert w3.cfx.default_account == ens_account.address
