from typing import TYPE_CHECKING


from conflux_web3 import Web3
from conflux_web3.contract.metadata import get_contract_metadata

if TYPE_CHECKING:
    from conflux_web3 import Web3


class TestEmbeddedContractMetadata:
    def test_get_contract_metadata(self):
        admin_contract_metadata = get_contract_metadata("AdminControl")
        assert isinstance(admin_contract_metadata["abi"], list)
        assert isinstance(admin_contract_metadata, dict)

    def test_contract_from_metadata(self, w3: Web3, use_testnet: bool):
        admin_contract = w3.cfx.contract(**get_contract_metadata("AdminControl"))
        assert admin_contract.abi
        assert w3.cfx.address.is_valid_base32(admin_contract.address)

        if use_testnet:

            usdt_contract = w3.cfx.contract(
                **get_contract_metadata("cUSDT", w3.cfx.chain_id)
            )
            assert usdt_contract.abi
            assert usdt_contract.bytecode
            assert w3.cfx.address.is_valid_base32(usdt_contract.address)
            assert usdt_contract.caller.symbol() == "cUSDT"

    def test_contract_from_name(self, w3: Web3, use_testnet: bool):
        admin_contract = w3.cfx.contract(name="AdminControl")
        assert admin_contract.abi
        assert w3.cfx.address.is_valid_base32(admin_contract.address)

        if use_testnet:
            usdt_contract = w3.cfx.contract(name="cUSDT")
            assert usdt_contract.abi
            assert usdt_contract.bytecode
            assert w3.cfx.address.is_valid_base32(usdt_contract.address)
            assert usdt_contract.caller.symbol() == "cUSDT"

        if w3.cfx.chain_id == 1:
            faucet = w3.cfx.contract(name="Faucet")
            assert faucet

    # TODO: test all embedded metadata functionalities
    def test_faucet_functions(self, w3: Web3):
        if w3.cfx.chain_id == 1:
            random_account = w3.account.create()
            w3.cfx.default_account = random_account
            faucet = w3.cfx.contract(name="Faucet")
            faucet.functions.claimCfx().transact().executed()
            assert w3.cfx.get_balance(w3.cfx.default_account) > 0
