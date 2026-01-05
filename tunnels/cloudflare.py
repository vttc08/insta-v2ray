from configuration import cloudflare_binary, bin_path, cloudflare_extra_args
from helper.check import check_binary
from helper.error import binary_not_found
import os
import logging
from tunnels.base import __BaseTunnel

logger = logging.getLogger(__name__)

def prerequisites():
    paths = [
        os.path.realpath(os.path.join(bin_path, cloudflare_binary)),
        os.path.realpath(cloudflare_binary)
    ]
    final_bin_path = next((p for p in paths if check_binary(p)), None)
    if not final_bin_path:
        error = binary_not_found(cloudflare_binary, __name__, paths=paths)
        logger.error(error)
        raise RuntimeError(error)
    return True

class Cloudflare(__BaseTunnel):
    limit = 99
    tunnel_url_regex = r"https://[^\s]+\.trycloudflare.com"
    cmdline = f"{cloudflare_binary} tunnel --url {{host}}:{{port}} --no-autoupdate {cloudflare_extra_args}"

    def __init__(self, host: str, port: int):
        super().__init__(host, port, prereq=prerequisites)
