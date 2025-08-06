import subprocess
import threading
import re
from configuration import pinggy_token, pinggy_url, pinggy_premium, pinggy_args
import queue
import logging
import time

logger = logging.getLogger(__name__)

class Pinggy:
    tunnels = 0
    def __init__(self, host: str, port: int, **provider_kwargs):
        self.host = host
        self.port = port
        self.provider_kwargs = provider_kwargs  # e.g., "--no-autoupdate", "--region" etc.
        self.process = None
        self.limit = 10 if pinggy_premium else 1
        self.tunnel_url = None
        if not pinggy_token:
            logger.error("PINGGY_TOKEN is not set in the environment variables.")
            raise ValueError("PINGGY_TOKEN is not set in the environment variables.")
        Pinggy.tunnels += 1
        if Pinggy.tunnels > self.limit:
            logger.error(f"Tunnel limit exceeded. Only {self.limit} tunnels can be started at a time for {self.__class__.__name__} {'premium' if pinggy_premium else 'free'} users.")
            raise RuntimeError(f"Tunnel limit exceeded. Only {self.limit} tunnels can be started at a time for {self.__class__.__name__} {'premium' if pinggy_premium else 'free'} users.")
        
                # use this code to implement logging
        self.log_queue = queue.Queue() # Create a queue to store log lines
        self.log_thread = None
        self._url_found_event = threading.Event() # Event to signal when URL is found

    def read_stdout(self):
        """Reads stdout continuously, puts lines into a queue, and looks for the tunnel URL."""
        for line in self.process.stdout:
            decoded_line = line.strip()
            self.log_queue.put(decoded_line) # Put the line into the queue
            logger.info(f"[{self.__class__.__name__}] {decoded_line}")

            match = re.search(r"https://[^\s]+\.free\.pinggy.link", decoded_line)
            if match:
                self.tunnel_url = match.group(0).replace("https://", "")
                logger.info(f"Tunnel URL found: {self.tunnel_url}")
                self._url_found_event.set() # Signal that the URL has been found
        self.log_queue.put(None)

    def start_tunnel(self):
        ssh_command = f"ssh -T -p 443 -R0:{self.host}:{self.port} -o StrictHostKeyChecking=no -o ServerAliveInterval=30 {pinggy_args} {pinggy_token}@{pinggy_url}"
        print(f"SSH command: {ssh_command}")
        self.process = subprocess.Popen(
            ssh_command.split(),
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
            logger.error("Tunnel URL not found in time.")
            raise RuntimeError("Tunnel URL not found in time.")

        return (self.process, self.tunnel_url)