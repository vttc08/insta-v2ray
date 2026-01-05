from helper.check import check_all_binaries
from helper.error import binary_not_found 
from configuration import bin_path, zrok_binary
import logging
import os
from tunnels.base import __BaseTunnel

logger = logging.getLogger(__name__)

def prerequisites():
    final_bin_path = check_all_binaries(bin_path, zrok_binary)
    # check binary status to be implmemented later
    if not final_bin_path:
        error = binary_not_found(zrok_binary, "zrok")
        logger.error(error)
        raise RuntimeError(error)
    return True

class Zrok(__BaseTunnel):
    limit = 99
    timeout = 15 # zrok may take longer to start
    tunnel_url_regex = r"https://[^\s]+\.zrok.io"
    zrok_binary_path = os.path.realpath(os.path.join(bin_path, zrok_binary))
    cmdline = f"{zrok_binary_path} share public {{host}}:{{port}}"
    def __init__(self, host: str, port: int):
        super().__init__(host, port, prereq=prerequisites)