import subprocess
import threading
import re
from helper.check import check_binary, is_docker, check_binary_status, check_node_runtime
from helper.error import binary_not_found, tunnel_url_not_found, tunnel_limits_exceeded, localhost_warning
from configuration import bin_path, localtunnel_binary
import time
import queue
import os
import logging

logger = logging.getLogger(__name__)

class LocalTunnel:
    tunnels = 0
    def __init__(self, host: str, port: int, **provider_kwargs):
        self.prerequisites()
        self.host = host
        self.port = port
        self.process = None
        self.tunnel_url = None
        self.log_queue = queue.Queue()  # Create a queue to store log lines
        self.log_thread = None
        self._url_found_event = threading.Event()  # Event to signal when URL is found
        self.limit = 5
        __class__.tunnels += 1
        if __class__.tunnels > self.limit:
            error = tunnel_limits_exceeded(self.__class__.__name__, self.limit)
            logger.error(error)
            raise RuntimeError(error)

    def prerequisites(self):
        if not check_node_runtime():
            error = "Node.js runtime is not installed or not found in PATH."
            logger.error(error)
            raise RuntimeError(error)
        paths = [
            localtunnel_binary
        ]
        self.bin = next((p for p in paths if check_binary(p)), None)
        if not self.bin:
            error = binary_not_found(localtunnel_binary, self.__class__.__name__, paths=paths)
            logger.error(error)
            raise RuntimeError(error)

    def read_stdout(self):
        """Reads stdout continuously, puts lines into a queue, and looks for the tunnel URL."""
        for line in self.process.stdout:
            decoded_line = line.strip()
            self.log_queue.put(decoded_line) # Put the line into the queue
            logger.info(f"[{self.__class__.__name__}] {decoded_line}")

            match = re.search(r"https://[^\s]+\.loca.lt", decoded_line)
            if match:
                self.tunnel_url = match.group(0).replace("https://", "")
                logger.info(f"Tunnel URL found: {self.tunnel_url}")
                self._url_found_event.set() # Signal that the URL has been found
        # when finished reading
        self.log_queue.put(None)

    def start_tunnel(self):
        command = f"{self.bin} --port {self.port}"
        logger.debug(f"Starting tunnel for {self.port} with command: {command}")
        self.process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redirect stderr to stdout so all output is in one stream
            text=True,
            bufsize=1 # Line-buffered output
        )

        self.log_thread = threading.Thread(target=self.read_stdout, daemon=True) # Set as daemon so it exits with main program
        self.log_thread.start()

        # Wait for the URL to be found, with a timeout
        start_time = time.time()
        while not self.tunnel_url and (time.time() - start_time) < 10 and self.process.poll() is None:
            time.sleep(0.1)
        
        if not self.tunnel_url:
            self.process.kill()
            error = tunnel_url_not_found(url="ts.net")
            logger.error(error)
            raise RuntimeError(error)

        return (self.process, self.tunnel_url)
    
    