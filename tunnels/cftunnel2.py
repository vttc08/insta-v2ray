import subprocess
import threading
import re
import time
import queue
import logging

logger = logging.getLogger(__name__)

class NewCFTunnel:
    tunnels = 0
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.process = None
        self.limit = 20
        self.tunnel_url = None
        NewCFTunnel.tunnels += 1
        if NewCFTunnel.tunnels > self.limit:
            raise RuntimeError(f"Maximum of {self.limit} tunnels can be started at a time.") # Modified error message for clarity

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

            match = re.search(r"https://[^\s]+\.trycloudflare.com", decoded_line)
            if match:
                self.tunnel_url = match.group(0).replace("https://", "")
                logger.info(f"Tunnel URL found: {self.tunnel_url}")
                self._url_found_event.set() # Signal that the URL has been found
        # when finished reading
        self.log_queue.put(None)

    def start_tunnel(self):
        mock_command = "python3 cloudflare.py" 
        logger.debug(f"Starting tunnel for {self.host}:{self.port} with command: {mock_command}")
        self.process = subprocess.Popen(
            mock_command.split(),
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

    
