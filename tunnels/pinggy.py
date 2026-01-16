import subprocess
import threading
import re
from configuration import pinggy_token, pinggy_url, pinggy_premium, pinggy_args
import queue
import logging
import time
from tunnels.base import __BaseTunnel

logger = logging.getLogger(__name__)

pinggy_counter = 0 # number of times it has been tried to reset

class Pinggy(__BaseTunnel):
    limit = 10 if pinggy_premium else 1
    tunnel_url_regex = r"https://[^\s]+\.free\.pinggy.link"
    cmdline = f"ssh -T -p 443 -R0:{{host}}:{{port}} -o StrictHostKeyChecking=no -o ServerAliveInterval=30 {pinggy_args} {pinggy_token}@{pinggy_url}"

    def start_tunnel(self):
        global pinggy_counter
        if pinggy_counter > 0:
            time.sleep(2) # wait for process to close fully
        p, u = super().start_tunnel()
        pinggy_counter += 1
        return(p, u)
