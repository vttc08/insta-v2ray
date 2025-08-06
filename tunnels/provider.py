import queue
import subprocess
import threading
import re
import time
import queue
import logging
from helper.check import check_binary, is_docker, check_binary_status
from helper.error import binary_not_found, tunnel_url_not_found, tunnel_limits_exceeded, binary_nonzero_exit, localhost_warning
from configuration import *

# import dotenv
# dotenv.load_dotenv()
# # you can also import the environments here

logger = logging.getLogger(__name__)

"""
How to implement a new provider from this template:
1. Copy this file.
2. Rename __ProviderTemplate to your provider name, do not include the __ prefix.
3. Most of the code is already implemented, look for the triple quotes and implement everything accordingly.
Some configurable parameters include
- tunnel limits, how many tunnels can be started at a time. e.g. 1
- prerequisites, checks that need to be done before starting the tunnel e.g. check binary exists
- url regex, the url that the tunnel provider outputs e.g. mytunnel.com
- command to start the tunnel e.g. mytunnel start --host {self.host} --port {self.port}
- environments and configuration from .env file e.g. API keys
"""

class __ProviderTemplate():
    tunnels = 0
    def __init__(self, host: str, port: int):
        """
        These are basic parameters, change tunnel limits if needed.
        """
        self.prerequisites()
        self.host = host
        self.port = port
        self.process = None
        self.log_queue = queue.Queue() 
        self.log_thread = None
        self._url_found_event = threading.Event() 
        self.limit = 9999
        __class__.tunnels += 1
        if __class__.tunnels > self.limit:
            error = tunnel_limits_exceeded(self.__class__.__name__, self.limit)
            logger.error(error)
            raise RuntimeError(error)

    def prerequisites(self):
        """
        Implement any checks needed before starting the tunnel, e.g. binary exists and works as expected.
        """
        pass

    def read_stdout(self):
        for line in self.process.stdout:
            decoded_line = line.strip()
            self.log_queue.put(decoded_line) 
            logger.info(f"[{self.__class__.__name__}] {decoded_line}")
            """
            Replace the regex with one that matches your tunnel URL format. Or implement your own logic to find the URL.
            """
            match = re.search(r"https://[^\s]+\.ts.net", decoded_line)
            if match:
                self.tunnel_url = match.group(0).replace("https://", "")
                logger.info(f"Tunnel URL found: {self.tunnel_url}")
                self._url_found_event.set() 
        self.log_queue.put(None)

    def start_tunnel(self):
        """
        Implement the command used to start the tunnel, or your own logic.
        """
        command = f""
        """
        You can use {self.host} and {self.port} in the command if needed as well as any other parameters.
        By default, everything in configuration.py is available here. If you're not using configuration.py, you can access environment variables directly using os.getenv().
        """
        # example_parameter = os.getenv("EXAMPLE_API_KEY", "default_value")
        logger.debug(f"Starting tunnel for {self.port} with command: {command}")
        self.process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.log_thread = threading.Thread(target=self.read_stdout, daemon=True)
        self.log_thread.start()

        start_time = time.time()
        while not self.tunnel_url and (time.time() - start_time) < 10 and self.process.poll() is None:
            time.sleep(0.1)
        
        if not self.tunnel_url:
            self.process.kill()
            error = tunnel_url_not_found(url="CustomProvider")
            logger.error(error)
            raise RuntimeError(error)

        return (self.process, self.tunnel_url)
    