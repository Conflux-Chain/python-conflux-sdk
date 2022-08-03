import os
from pathlib import Path
# abs path of _utils
util_path = Path(__file__).parents[0]
LOCAL_RUN_PATH = os.path.join(util_path, "local_run")

TAG = "latest"
REPO_NAME = "confluxchain/conflux-rust"
IMAGE_FULL_NAME = f"{REPO_NAME}:{TAG}"
LOCAL_NODE_NAME = "python-sdk-env"
LOCAL_HOST = "127.0.0.1"
PORT = "12537"

# if __name__ == "__main__":
    
#     print(path)
    
