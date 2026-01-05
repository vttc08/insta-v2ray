import subprocess
import threading
import re
from configuration import pinggy_token, pinggy_url, pinggy_premium, pinggy_args
import queue
import logging
import time
from tunnels.base import __BaseTunnel

logger = logging.getLogger(__name__)

class Pinggy(__BaseTunnel):
    limit = 10 if pinggy_premium else 1
    tunnel_url_regex = r"https://[^\s]+\.free\.pinggy.link"
    cmdline = f"ssh -T -p 443 -R0:{{host}}:{{port}} -o StrictHostKeyChecking=no -o ServerAliveInterval=30 {pinggy_args} {pinggy_token}@{pinggy_url}"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)