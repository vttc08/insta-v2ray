import subprocess
import threading
import re
import time
import queue
import logging
from helper.error import tunnel_limits_exceeded, tunnel_url_not_found

logger = logging.getLogger(__name__)

class __BaseTunnel:
    tunnels = 0
    def __init__(self, host: str, port: int, disabled: bool = False):
        self.host = host
        self.port = port
        self.process = None
        self.tunnel_url = None

        # use this code to implement logging
        self.log_queue = queue.Queue() # Create a queue to store log lines
        self.log_thread = None
        self._url_found_event = threading.Event() # Event to signal when URL is found

        child = type(self)
        if child.tunnels >= child.limit:
            logger.error(tunnel_limits_exceeded(child.__name__, child.limit))
            raise RuntimeError(tunnel_limits_exceeded(child.__name__, child.limit))
        child.tunnels += 1

        if hasattr(child, 'timeout'):
            self.timeout = child.timeout
        else:
            self.timeout = 10  # default timeout

        if disabled:
            raise RuntimeError(f"{child.__name__} is disabled due to configuration issue, please check the logs.")

    def read_stdout(self):
        """Reads stdout continuously, puts lines into a queue, and looks for the tunnel URL."""
        for line in self.process.stdout:
            decoded_line = line.strip()
            self.log_queue.put(decoded_line) # Put the line into the queue
            logger.info(f"[{self.__class__.__name__}] {decoded_line}")

            match = re.search(self.tunnel_url_regex, decoded_line)
            if match:
                self.tunnel_url = match.group(0).replace("https://", "")
                logger.info(f"Tunnel URL found: {self.tunnel_url}")
                self._url_found_event.set() # Signal that the URL has been found
        # when finished reading
        self.log_queue.put(None)

    def start_tunnel(self):
        mock_command = self.cmdline.format(host=self.host, port=self.port)
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
        while not self.tunnel_url and (time.time() - start_time) < self.timeout and self.process.poll() is None:
            time.sleep(0.1)
        
        if not self.tunnel_url:
            self.process.kill()
            error = tunnel_url_not_found(provider=self.__class__.__name__)
            raise RuntimeError(error)

        return (self.process, self.tunnel_url)