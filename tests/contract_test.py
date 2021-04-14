from conflux import (
    Conflux,
    HTTPProvider,
)
import json
from cfx_address import Address
import os
current_path = os.path.dirname(os.path.abspath(__file__))

provider = HTTPProvider('https://test.confluxrpc.com')
c = Conflux(provider)

with open(current_path + os.path.sep + 'crc20_abi.json') as json_file:
    abi_json = json.load(json_file)

token_address = 'cfxtest:acattk1yzt7b8z01m8urnmytst1z0wv0tuvczsyr32'
user_address = 'cfxtest:aak2rra2njvd77ezwjvx04kkds9fzagfe6d5r8e957'

def test_contract_call():
    balance = c.call_contract_method(token_address, abi_json["abi"], "balanceOf", Address(user_address).eth_checksum_address)
    print(balance)

def test_contract_update():
    contract = c.contract(token_address, abi_json["abi"])
    data = contract.encodeABI(fn_name="transfer", args=["0x13d2bA4eD43542e7c54fbB6c5fCCb9f269C1f94C", 100])
    print(data)