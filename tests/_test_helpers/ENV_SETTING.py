import json

TAG = "latest"
REPO_NAME = "confluxchain/conflux-rust"
IMAGE_FULL_NAME = f"{REPO_NAME}:{TAG}"
LOCAL_NODE_NAME = "python-sdk-env"
LOCAL_HOST = "127.0.0.1"
PORT = "12537"

erc20_metadata = json.load(open("tests/_test_helpers/ERC20.json"))
