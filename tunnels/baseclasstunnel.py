from tunnels.base import __BaseTunnel
import logging
from helper.check import check_all_binaries
from configuration import bin_path, cloudflare_binary

logger = logging.getLogger(__name__)

class CloudflareBaseClass(__BaseTunnel):
    """
    This is an example using the new base class method.
    """
    limit = 1
    tunnel_url_regex = r"https://[^\s]+\.trycloudflare.com"
    cmdline = "python3 cloudflare.py"
    timer = {"keepalive": 10,"expire": 18}

    def __init__(self, host: str, port: int):
        super().__init__(host, port)