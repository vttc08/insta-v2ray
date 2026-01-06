from configuration import cloudflare_binary, bin_path, cloudflare_extra_args

import os
import logging
from tunnels.base import __BaseTunnel
from helper.check import validate_provider, BinaryCheck

logger = logging.getLogger(__name__)

checks = [BinaryCheck(bin_path, cloudflare_binary, "cloudflared")]
is_enabled, ctx = validate_provider(checks, __name__)
cf_bin = ctx.get("cloudflared_binary", cloudflare_binary)

class Cloudflare(__BaseTunnel):
    limit = 99
    tunnel_url_regex = r"https://[^\s]+\.trycloudflare.com"
    cmdline = f"{cf_bin} tunnel --url {{host}}:{{port}} --no-autoupdate {cloudflare_extra_args}"

    def __init__(self, host: str, port: int):
        super().__init__(host, port, disabled=not is_enabled)
