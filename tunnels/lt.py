from helper.check import check_binary, check_node_runtime
from helper.error import binary_not_found
from configuration import localtunnel_binary
import logging
from tunnels.base import __BaseTunnel

logger = logging.getLogger(__name__)

def prerequisites():
    if not check_node_runtime():
        error = "Node.js runtime is not installed or not found in PATH."
        logger.error(error)
        raise RuntimeError(error)
    paths = [
        localtunnel_binary
    ]
    final_bin_path = next((p for p in paths if check_binary(p)), None)
    if not final_bin_path:
        error = binary_not_found(localtunnel_binary, __name__, paths=paths)
        logger.error(error)
        raise RuntimeError(error)
    return True

class LocalTunnel(__BaseTunnel):
    limit = 5
    tunnel_url_regex = r"https://[^\s]+\.loca.lt"
    cmdline = f"{localtunnel_binary} --port {{port}}"
    def __init__(self, host: str, port: int, prereq=prerequisites):
        super().__init__(host, port, prereq=prereq)
