import queue
import subprocess
import threading
import re
from tunnels.base import __BaseTunnel
import logging

logger = logging.getLogger(__name__)

class BadTunnel(__BaseTunnel):
    limit = 99
    tunnel_url_regex = r"https://[^\s]+\.test.com"
    shell_cmd = "for i in 1 2 3 4 5; do echo 'Please authorize before creating a tunnel.'; sleep 1; done"
    cmdline = "bash -c '" + shell_cmd + "'"
    timeout = 12

    def __init__(self, host: str, port: int):
        super().__init__(host, port)


    