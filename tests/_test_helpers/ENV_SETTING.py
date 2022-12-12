import json
import os

TAG = "latest"
TESTNET_TAG = "2.1.0-testnet"
REPO_NAME = "confluxchain/conflux-rust"
DEV_IMAGE_FULL_NAME = f"{REPO_NAME}:{TAG}"
TESTNET_IMAGE_FULL_NAME = f"{REPO_NAME}:{TESTNET_TAG}"
LOCAL_NODE_NAME = "python-sdk-env"
TESTNET_NODE_NAME = "python-sdk-env-testnet"
LOCAL_HOST = "127.0.0.1"
PORT = "12537"
TESTNET_HOST_PORT = "12637"

TESTNET_CONFIG_DIR = os.path.join(
    os.path.dirname(__file__), 
    "testnet"
)
VOLUMES = {
    TESTNET_CONFIG_DIR: {
        "bind": "/root/run",
        "mode": "rw",
    }
}

HELPER_DIR = os.path.dirname(__file__)
