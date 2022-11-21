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

from cfx_account import Account
from conflux_web3 import (
    Web3,
)
from conflux_web3._utils.decorators import (
    cached_property,
)
from tests._test_helpers.ENV_SETTING import (
    DEV_IMAGE_FULL_NAME,
    TESTNET_IMAGE_FULL_NAME,
    LOCAL_NODE_NAME,
    TESTNET_NODE_NAME,
    LOCAL_HOST,
    PORT,
    VOLUMES,
    TESTNET_HOST_PORT
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
    
def pull_image(client: docker.client.DockerClient, image_name:str):
    try:
        client.images.get(image_name)
    except ImageNotFound:
        client.images.pull(image_name)
    
def get_existed_container(client: docker.client.DockerClient, node_name: str):

    # remove the container if existence
    try:
        container = client.containers.get(node_name)
        # container.remove(force=True)  # type: ignore
        return container
    except NotFound:
        return None
     
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
    """ using docker to start a private local node.
    if container with node_name (default as "python-sdk-env") already exists, no extra work needs be done
    else pull image and create environment
    """
    def __init__(self, image_name=DEV_IMAGE_FULL_NAME, node_name=LOCAL_NODE_NAME):
        self._image_name = image_name
        self._node_name = node_name
        self._url = f"http://{LOCAL_HOST}:{PORT}"
        self._client = docker.from_env()
        
        if container := get_existed_container(self._client, self._node_name):
            self._container = container
        else:
            pull_image(self._client, self._image_name)
            self._container = self._client.containers.run(self._image_name, 
                                                        name=self._node_name, 
                                                        detach=True, 
                                                        # auto_remove=True,
                                                        ports={
                                                            f"{PORT}/tcp": f"{PORT}"
                                                        })
            self._wait_for_start()

    @cached_property
    def secrets(self) -> List[str]:
        raw = self._container.exec_run("cat genesis_secret.txt").output.decode("utf-8")  # type: ignore
        secrets = raw.split("\n")
        return secrets
    
    def _wait_for_start(self):
        interval = 1
        max_try = 120
        print("starting test node")
        # time.sleep(10)
        
        for i in range(max_try):
            try:
                status = connect_to_server(self.url)
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

class LocalTestnetNode(LocalNode):
    def __init__(self, image_name=TESTNET_IMAGE_FULL_NAME, node_name=TESTNET_NODE_NAME, volumes=VOLUMES):
        self._image_name = image_name
        self._node_name = node_name
        self._url = f"http://{LOCAL_HOST}:{TESTNET_HOST_PORT}"
        self._client = docker.from_env()
        
        if container := get_existed_container(self._client, self._node_name):
            self._container = container
        else:
            pull_image(self._client, self._image_name)
            self._container = self._client.containers.run(self._image_name, 
                                                        name=self._node_name, 
                                                        detach=True, 
                                                        # auto_remove=True,
                                                        volumes=volumes,
                                                        ports={
                                                            f"{PORT}/tcp": f"{TESTNET_HOST_PORT}" # use a different port on host
                                                        })
            self._wait_for_start()
    
    @cached_property
    def secrets(self) -> List[str]:
        secrets = [Account.create().privateKey]
        return secrets 
    
    def _wait_for_embedded_tx_finished(self):
        return

class RemoteTestnetNode(BaseNode):
    def __init__(self) -> None:
        self._url = os.environ.get("TESTNET_URL", None) or 'https://test.confluxrpc.com'
    
    @cached_property
    def secrets(self) -> List[str]:
        testnet_secret = os.environ.get("TESTNET_SECRET", None)
        if not testnet_secret:
            return [Account.create().privateKey]
        return [testnet_secret]
