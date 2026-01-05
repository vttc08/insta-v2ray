from tunnels.base import __BaseTunnel
import logging
from helper.check import check_binary_status

logger = logging.getLogger(__name__)

class CloudflareBaseClass(__BaseTunnel):
    """
    This is an example using the new base class method.
    """
    limit = 1
    tunnel_url_regex = r"https://[^\s]+\.trycloudflare.com"
    cmdline = "python3 cloudflare.py"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)