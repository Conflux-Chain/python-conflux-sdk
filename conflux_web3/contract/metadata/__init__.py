import json
from pathlib import (
    Path
)
from typing import (
    Dict,
    Optional
)
from toolz import (
    keyfilter
)

from cfx_address.utils import (
    validate_address_agaist_network_id
)

METADATA_DIR = Path(__file__).parent

# DEPLOYMENT_INFO
DEPLOYMENT_INFO = {
    "AdminControl": "0x0888000000000000000000000000000000000000",
    "SponsorWhitelistControl": "0x0888000000000000000000000000000000000001",
    "Staking": "0x0888000000000000000000000000000000000002",
    "ConfluxContext": "0x0888000000000000000000000000000000000003",
    "PoSRegister": "0x0888000000000000000000000000000000000005",
    "CrossSpaceCall": "0x0888000000000000000000000000000000000006",
    "ParamsControl": "0x0888000000000000000000000000000000000007",
    "Create2Factory": "0x8A3A92281Df6497105513B18543fd3B60c778E40",
    "ERC1820": "0x88887eD889e776bCBe2f0f9932EcFaBcDfCd1820",
    "Faucet": "cfxtest:acejjfa80vj06j2jgtz9pngkv423fhkuxj786kjr61",
    "cUSDT": {
        1: "cfxtest:acepe88unk7fvs18436178up33hb4zkuf62a9dk1gv",
        1029: "cfx:acf2rcsh8payyxpg6xj7b0ztswwh81ute60tsw35j7",
    },
    "FC": {
        1: "cfxtest:achkx35n7vngfxgrm7akemk3ftzy47t61yk5nn270s",
        1029: "cfx:achc8nxj7r451c223m18w2dwjnmhkd6rxawrvkvsy2",
    }
}

METADATA_INFO = {
    "cUSDT": "ERC20",
    "FC": "ERC20",
}

def list_embedded_contract_names():
    pass

# TODO: normalize metadata["bin"] to metadata["bytecode"]
def get_contract_metadata(contract_name: str, chain_id: Optional[int]=None) -> Dict:
    metadata_path = METADATA_DIR / f"{METADATA_INFO.get(contract_name, contract_name)}.json"
    with open(metadata_path) as f:
        metadata = json.load(f)
    metadata = keyfilter(lambda x: x in ["abi", "bytecode"], metadata)
    address_info = DEPLOYMENT_INFO.get(contract_name, None)
    if address_info is not None:
        if isinstance(address_info, str):
            validate_address_agaist_network_id(address_info, chain_id, accept_hex=True)
            metadata["address"] = address_info
        elif isinstance(address_info, dict):
            metadata["address"] = address_info[chain_id]
        else:
            raise Exception("unexpected error")
    return metadata
