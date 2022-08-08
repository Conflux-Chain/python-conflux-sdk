from abc import ABC
import json
import os
from typing import (
    List
)
import time
import urllib3
import functools

import docker
from docker.errors import (
    ImageNotFound,
    NotFound
)

from conflux_web3 import (
    Web3,
)
from tests._test_helpers.ENV_SETTING import (
    IMAGE_FULL_NAME,
    LOCAL_NODE_NAME,
    LOCAL_HOST,
    PORT,
)

def setup_docker_env(client: docker.client.DockerClient, image_name:str, node_name: str):
    try:
        client.images.get(image_name)
    except ImageNotFound:
        client.images.pull(image_name)
    
    # remove the container if existence
    try:
        container = client.containers.get(node_name)
        container.remove(force=True)  # type: ignore
        time.sleep(10)
    except NotFound:
        pass # do nothing
     
def connect_to_server(url):
    # http = urllib3.PoolManager()
    payload = {
        "method": "cfx_getStatus",
        "params": [],
        "jsonrpc": "2.0",
        "id": 1,
    }
    header = {
        "Content-Type": "application/json"
    }
    data = json.dumps(payload)
    http = urllib3.PoolManager()
    res = http.request('POST', url, body=data, headers=header, retries=False)
    result = json.loads(res.data)["result"]
    
    return result

class BaseNode(ABC):
    def __init__(self):
        self._url = None
    
    @property
    def url(self):
        return self._url

    def secrets(self) -> List[str]:
        return []
    
    def exit(self):
        pass

class LocalNode(BaseNode):
    """ using docker to start a private local node
    """
    def __init__(self, image_name = None, already_exist=False):
        self._image_name = image_name or IMAGE_FULL_NAME
        self._node_name = LOCAL_NODE_NAME
        self._url = f"http://{LOCAL_HOST}:{PORT}"
        self._client = docker.from_env()
        
        if already_exist:
            self._container = self._client.containers.get(LOCAL_NODE_NAME)
        else:
            setup_docker_env(self._client, self._image_name, self._node_name)
            self._container = self._client.containers.run(self._image_name, 
                                                        name=self._node_name, 
                                                        detach=True, 
                                                        # auto_remove=True,
                                                        ports={
                                                            f"{PORT}/tcp": f"{PORT}"
                                                        }) 
            self._wait_for_start()

    @functools.cached_property
    def secrets(self) -> List[str]:
        raw = self._container.exec_run("cat genesis_secret.txt").output.decode("utf-8")  # type: ignore
        secrets = raw.split("\n")
        secrets.append("0x46b9e861b63d3509c88b7817275a30d22d62c8cd8fa6486ddee35ef0d8e0495f")
        return secrets
    
    def _wait_for_start(self):
        interval = 1
        max_try = 30
        print("starting test node")
        # time.sleep(10)
        
        for i in range(max_try):
            try:
                status = connect_to_server(self.url)
                # w3 = Web3(Web3.HTTPProvider(url))
                # status = w3.cfx.get_status()
                
                if int(status["epochNumber"], 16) >= 1:
                    return self._wait_for_embedded_tx_finished()
                time.sleep(interval)
            except:
                time.sleep(interval)
            # finally:
            #     time.sleep(interval)
        raise ConnectionError("Not connected to node")
    
    def _wait_for_embedded_tx_finished(self):
        interval = 1
        max_try = 300
        # time.sleep(10)
        w3 = Web3(Web3.HTTPProvider(self.url))
        account = w3.account.from_key(self.secrets[0], w3.cfx.chain_id)
        for i in range(max_try):
            if w3.cfx.get_next_nonce(account.address) >= 10:
                return
            time.sleep(interval)
        raise RuntimeError("Exceeds max wait time")
    
    def exit(self):
        if self._container:
            self._container.remove(force=True)  # type: ignore
        if self._client:
            self._client.close()
        

class RemoteTestnetNode(BaseNode):
    def __init__(self) -> None:
        self._url = 'https://test.confluxrpc.com'
    
    @functools.cached_property
    def secrets(self) -> List[str]:
        testnet_secret = os.environ.get("TESTNET_SECRET")
        if not testnet_secret:
            raise RuntimeError("Environment secret is not set")
        return [testnet_secret]
        