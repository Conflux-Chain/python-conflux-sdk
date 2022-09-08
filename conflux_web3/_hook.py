from cfx_utils.post_import_hook import when_imported
from conflux_web3._utils.decorators import (
    cfx_web3_condition,
    conditional_func,
    conditional_post_func,
)

@when_imported("web3._utils.contracts")
def hook_encode_abi(mod):
    from conflux_web3._utils.contracts import cfx_encode_abi
    mod.encode_abi = conditional_func(
        cfx_encode_abi,
        cfx_web3_condition
    )(mod.encode_abi)

@when_imported("web3.contract")
def hook_parse_block_identifier(mod):
    from conflux_web3.contract import cfx_parse_block_identifier
    mod.parse_block_identifier = conditional_func(
        cfx_parse_block_identifier,
        cfx_web3_condition
    )(mod.parse_block_identifier)
    
@when_imported("ethpm.package")
def hook_ethpm_package(mod):
    from cfxpm.package import set_conflux_linkable_contract
    mod.Package.__init__ = conditional_post_func(
        set_conflux_linkable_contract,
        cfx_web3_condition
    )(mod.Package.__init__)
