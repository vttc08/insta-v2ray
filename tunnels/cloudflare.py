import subprocess
import threading
import re
from configuration import cloudflare_binary, bin_path, cloudflare_extra_args
from helper.check import check_binary
from helper.error import binary_not_found, tunnel_url_not_found
import time
import queue
import os
import logging

logger = logging.getLogger(__name__)

class Cloudflare:
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
        
    def prerequisites(self):
        paths = [
            os.path.realpath(os.path.join(bin_path, cloudflare_binary)),
            os.path.realpath(cloudflare_binary)
        ]
        self.bin = next((p for p in paths if check_binary(p)), None)
        if not self.bin:
            error = binary_not_found(cloudflare_binary, self.__class__.__name__, paths=paths)
            logger.error(error)
            raise RuntimeError(error)
        
    def read_stdout(self):
        """Reads stdout continuously, puts lines into a queue, and looks for the tunnel URL."""
        for line in self.process.stdout:
            decoded_line = line.strip()
            self.log_queue.put(decoded_line) # Put the line into the queue
            logger.info(f"[{self.__class__.__name__}] {decoded_line}")

            _d = [0x74,0x72,0x79,0x63,0x6c,0x6f,0x75,0x64,0x66,0x6c,0x61,0x72,0x65,0x2e,0x63,0x6f,0x6d]
            __d = ''.join(map(chr, _d))
            _p = ''.join([chr(x) for x in [0x5b,0x5e,0x5c,0x73,0x5d,0x2b,0x5c,0x2e]])  # [^\s]+\.
            _h = ''.join([chr(x) for x in [0x68,0x74,0x74,0x70,0x73,0x3a,0x2f,0x2f]])  # https://
            __r = _h + _p + re.escape(__d)
            match = re.search(__r, decoded_line)
            if match:
                self.tunnel_url = match.group(0).replace("https://", "")
                logger.info(f"Tunnel URL found: {self.tunnel_url}")
                self._url_found_event.set() # Signal that the URL has been found
        # when finished reading
        self.log_queue.put(None)

    def start_tunnel(self):
        command = f"{self.bin} tunnel --url {self.host}:{self.port} --no-autoupdate {cloudflare_extra_args}"
        logger.debug(f"Starting tunnel for {self.host}:{self.port} with command: {command}")
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
            error = tunnel_url_not_found(url="trycloudflare.com")
            logger.error(error)
            raise RuntimeError(error)

        return (self.process, self.tunnel_url)
    