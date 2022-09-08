from ethpm import Package, ASSETS_DIR

def test_contract_factory(w3):
    # ethpm_spec_dir = get_ethpm_spec_dir()
    erc20_manifest_path = ASSETS_DIR / 'standard-token' / 'with_bytecode_v3.json'
    # erc20_manifest_path = '/Users/conflux-y/Documents/code/web3.py/ethpm/assets/standard-token/with_bytecode_v3.json'
    ERC20Package = Package.from_file(erc20_manifest_path, w3)
    assert isinstance(ERC20Package, Package)
    
    factory = ERC20Package.get_contract_factory("StandardToken") # type: ignore
    
    assert factory
