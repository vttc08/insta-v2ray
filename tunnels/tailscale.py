import subprocess
import threading
import re
from helper.check import check_binary, is_docker, check_binary_status
from helper.error import binary_not_found, tunnel_url_not_found, tunnel_limits_exceeded, binary_nonzero_exit, localhost_warning
from configuration import tailscale_mode, bin_path
import time
import queue
import os
import logging

logger = logging.getLogger(__name__)

class __TailscaleCLI:
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
        self.limit = 1
        __class__.tunnels += 1
        if __class__.tunnels > self.limit:
            error = tunnel_limits_exceeded(self.__class__.__name__, self.limit)
            logger.error(error)
            raise RuntimeError(error)

    def prerequisites(self):
        if running_in_docker or not check_binary("tailscale"):
            error = binary_not_found("tailscale", self.__class__.__name__)
            logger.error(error)
            raise RuntimeError(error)
        if not check_binary_status("tailscale funnel"):
            error = binary_nonzero_exit("tailscale", self.__class__.__name__)
            logger.error(error)
            raise RuntimeError(error)

    def read_stdout(self):
        """Reads stdout continuously, puts lines into a queue, and looks for the tunnel URL."""
        for line in self.process.stdout:
            decoded_line = line.strip()
            self.log_queue.put(decoded_line) # Put the line into the queue
            logger.info(f"[{self.__class__.__name__}] {decoded_line}")

            match = re.search(r"https://[^\s]+\.ts.net", decoded_line)
            if match:
                self.tunnel_url = match.group(0).replace("https://", "")
                logger.info(f"Tunnel URL found: {self.tunnel_url}")
                self._url_found_event.set() # Signal that the URL has been found
        # when finished reading
        self.log_queue.put(None)

    def start_tunnel(self):
        command = f"tailscale funnel {self.port}"
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
    
class __TailscaleDocker:
    def start_tunnel(self):
        # Placeholder for Docker-based Tailscale tunnel start logic
        raise NotImplementedError("Docker-based Tailscale tunnel start is not implemented yet.")
    

running_in_docker = is_docker()
docker_present = check_binary("docker") and subprocess.call(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
docker_capable = running_in_docker and docker_present

if not tailscale_mode:
    if docker_capable:
        tailscale_mode = "docker"
        logger.info("TAILSCALE_MODE not set, but found Docker capabilities. Defaulting to 'docker' mode.")
    else:
        logger.error(f"TAILSCALE_MODE is not set. Please set it to 'cli' or 'docker'. This provider will not be available.")

ts_class = __TailscaleDocker if tailscale_mode == "docker" else __TailscaleCLI if tailscale_mode == "cli" else str

logger.warning(localhost_warning)

class Tailscale(ts_class):
    pass