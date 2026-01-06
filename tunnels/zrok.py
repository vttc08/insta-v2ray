from configuration import bin_path, zrok_binary
import logging
from tunnels.base import __BaseTunnel
from helper.check import validate_provider, BinaryCheck

logger = logging.getLogger(__name__)

checks = [BinaryCheck(bin_path, zrok_binary, "zrok")]
is_enabled, ctx = validate_provider(checks, __name__)
z_bin = ctx.get("zrok_binary", zrok_binary)

class Zrok(__BaseTunnel):
    limit = 99
    timeout = 15 # zrok may take longer to start
    tunnel_url_regex = r"https://[^\s]+\.zrok.io"
    cmdline = f"{z_bin} share public {{host}}:{{port}}"

    def __init__(self, host: str, port: int):
        super().__init__(host, port, disabled=not is_enabled)