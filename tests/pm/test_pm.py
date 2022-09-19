from ethpm import Package, ASSETS_DIR

def test_contract_factory(w3):
    # ethpm_spec_dir = get_ethpm_spec_dir()
    escrow_manifest_path = ASSETS_DIR / 'escrow' / 'with_bytecode_v3.json'
    # erc20_manifest_path = '/Users/conflux-y/Documents/code/web3.py/ethpm/assets/standard-token/with_bytecode_v3.json'
    escrow_package = Package.from_file(escrow_manifest_path, w3)
    assert isinstance(escrow_package, Package)
    
    factory = escrow_package.get_contract_factory("Escrow") # type: ignore
    
    assert factory
