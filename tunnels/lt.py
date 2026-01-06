from helper.check import check_binary, validate_provider, NodeRuntimeCheck, CustomCheck
from configuration import localtunnel_binary
import logging
from tunnels.base import __BaseTunnel

logger = logging.getLogger(__name__)

checks = [
    NodeRuntimeCheck(),
    CustomCheck(check_binary,"lt")
]
is_enabled, ctx = validate_provider(checks, __name__)
lt_bin = ctx.get("lt_bin", localtunnel_binary)


class LocalTunnel(__BaseTunnel):
    limit = 5
    tunnel_url_regex = r"https://[^\s]+\.loca.lt"
    cmdline = f"{lt_bin} --port {{port}}"
    
    def __init__(self, host: str, port: int):
        super().__init__(host, port, disabled=not is_enabled)
