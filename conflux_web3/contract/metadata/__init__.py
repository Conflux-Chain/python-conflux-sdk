import json
import os
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

from ens import (
    abis,
)
from cfx_address.utils import (
    validate_address_agaist_network_id
)
from conflux_web3.exceptions import (
    DeploymentInfoNotFound,
    ContractMetadataNotFound
)

METADATA_DIR = Path(__file__).parent

# DEPLOYMENT_INFO
DEPLOYMENT_INFO = {
    "AdminControl": "0x0888000000000000000000000000000000000000",
    "SponsorWhitelistControl": "0x0888000000000000000000000000000000000001",
    "Staking": "0x0888000000000000000000000000000000000002",
    # "ConfluxContext": "0x0888000000000000000000000000000000000003",
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
    },
    "ENS": {
        1: "cfxtest:acemru7fu1u8brtyn3hrtae17kbcd4pd9u2m761bta",
        1029: "cfx:acemru7fu1u8brtyn3hrtae17kbcd4pd9uwbspvnnm",
    }
}

METADATA_INFO = {
    "cUSDT": "ERC20",
    "FC": "ERC20",
}

def list_embedded_contract_names():
    pass

# TODO: normalize metadata["bin"] to metadata["bytecode"]
# TODO: return type as TypedDict
def get_contract_metadata(
    contract_name: str, 
    chain_id: Optional[int]=None, 
    with_deployment_info: Optional[bool]=None
) -> Dict:
    """
    _summary_

    Parameters
    ----------
    contract_name : str
        the name of the contract
    chain_id : Optional[int], optional
        _description_, by default None
    with_deployment_info : Optional[bool], optional
        whether "address" will be in the returned Dict.
        if is None, this api will try to fill the address field if possible, and no exception will be raised
        if is False, this api will never fill the address field.
        if is True, this api will always try to fill the address field, and may raise exceptions
        by default None

    Returns
    -------
    Dict
        _description_

    Raises
    ------
    ContractMetadataNotFound
        _description_
    DeploymentInfoNotFound
        _description_
    """
    try:
        metadata_path = METADATA_DIR / f"{METADATA_INFO.get(contract_name, contract_name)}.json"
        if not os.path.exists(metadata_path):
            raise ContractMetadataNotFound(f"Metadata for {contract_name} not found")
        with open(metadata_path) as f:
            metadata = json.load(f)
        metadata = keyfilter(lambda x: x in ["abi", "bytecode"], metadata)
    except ContractMetadataNotFound as e:
        abi = getattr(abis, contract_name, None)
        if abi:
            metadata = {
                "abi": abi
            }
        else:
            raise e
    # process address field if with_deployment_info is True or None
    if with_deployment_info is not False:
        if contract_name not in DEPLOYMENT_INFO:
            if with_deployment_info is True:
                raise DeploymentInfoNotFound(f"Deployment info for {contract_name} not found")
            return metadata
        address_info = DEPLOYMENT_INFO[contract_name]
        # "AdminControl": "0x0888000000000000000000000000000000000000"
        if isinstance(address_info, str):
            validate_address_agaist_network_id(address_info, chain_id, accept_hex=True)
            metadata["address"] = address_info
        # "cUSDT": {
        #     1: "cfxtest:acepe88unk7fvs18436178up33hb4zkuf62a9dk1gv",
        #     1029: "cfx:acf2rcsh8payyxpg6xj7b0ztswwh81ute60tsw35j7",
        # }
        elif isinstance(address_info, dict):
            if not chain_id:
                raise ValueError(f"{contract_name}'s deployment info varies with different chain id, chain id should be specified")
            if with_deployment_info and (chain_id not in address_info):
                raise DeploymentInfoNotFound(f"Deployment info for {contract_name} of chain id {chain_id} not found")
            metadata["address"] = address_info[chain_id]
        else:
            raise Exception("unexpected error")
    return metadata
