import queue
import subprocess
import threading
import re
import time
import queue
import logging
from helper.check import validate_provider, CustomCheck, BinaryCheck, NodeRuntimeCheck, DockerCheck
from helper.error import tunnel_url_not_found, tunnel_limits_exceeded
from configuration import *
from tunnels.base import __BaseTunnel

# import dotenv
# dotenv.load_dotenv()
# # you can also import the environments here

logger = logging.getLogger(__name__)

"""
How to implement a new provider from this template:
1. Copy this file.
2. Rename __ProviderTemplate to your provider name, do not include the __ prefix.
3. Follow the comments in the instructions below to define parameters that best suits your tunnel provider.
Optional: If the default base class do not meet the requirement, you can replace the following methods 
- reading stdout logs from tunnel providers
- procedure to start the tunnel provider program
Some configurable parameters include
- tunnel limits, how many tunnels can be started at a time. e.g. 1
- prerequisites, checks that need to be done before starting the tunnel e.g. check binary exists
- url regex, the url that the tunnel provider outputs e.g. mytunnel.com
- command to start the tunnel e.g. mytunnel start --host {self.host} --port {self.port}
- environments and configuration from .env file e.g. API keys
"""

"""
Below is a minimal implementation for a custom provider using the new __BaseTunnel inheritance.
"""

some_variable = "" ### Optional. You can define any Python variable or logic here for your custom Provider class

class __ProviderTemplate(__BaseTunnel):
    limit = 10 
    ### Required. How many tunnels can be started at the same time
    tunnel_url_regex = r'https://[^\s]+\.some.tunnel.domain' 
    ### Required. The regular expression the program looks for when parsing the logs of the tunnel provider to get the public URL from the tunnel provider
    ### You can test your regular expression at https://regexr.com/
    cmdline = f"/usr/bin/sometunnel --host {{host}}:{{port}} {some_variable}" 
    ### Required. The shell command required to start the tunnel
    ### - you'll need to use {{}} for host and port to pass these parameters into the command

"""
You can use the following code to implement checks before initialize the tunnel. If a provider fail these checks, it will not be enabled. Make sure to uncomment the lines.
""" 
# checks = [
#     BinaryCheck(bin_path, cloudflare_binary, "cloudflared"),
#     NodeRuntimeCheck(),
#     CustomCheck(lambda x: True if x > 5 else False, x=6)
# ]

# is_enabled, ctx = validate_provider(checks, __name__)
# cf_bin = ctx.get("cloudflared_binary", cloudflare_binary)

"""
You'll also need to add these lines to your custom provider class.
"""

    # def __init__(self, host: str, port: int):
    #     super().__init__(host, port, disabled=not is_enabled)

"""
BinaryCheck(bin_path, bin_full_path_or_name, bin_readable_name)
    - bin_path: the folder which store binaries, e.g. /usr/bin, ./bin
    - bin_full_path_or_name: full path of the binary, or a binary name, e.g. cloudflared, which will be joined with bin_path to produce e.g. ./bin/cloudflared
    - bin_readable_name: human readable name of the binary, used for display and logging

NodeRuntimeCheck() - check if NodeJS is installed and working

CustomCheck(function, arguments) - provide custom functions for checking requirements
    - function: can be lambda one-line function or a defined function
    - arguments: any positional *args or keyword **kwargs passed into the function
The function must return True if everything passes, and None or False for failure cases
def hello(one, two):
    return True | False
To run the function hello(one="hello", two="world") as a check, you'll pass CustomCheck(hello, one="hello", two="world")
"""



"""
You can still use the old method for implementing your custom provider, or override specific methods.
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
        """
        Your custom method must set self.tunnel_url with a valid link, and optionally implement logging. This method only take self and it has access to all the self attribute such as self.process: Subprocess.Popen
        """
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
        Implement the command used to start the tunnel, or your own logic. The method takes self, has access to its attribute and must return a tuple of (self.process: Subprocess.Popen, self.tunnel_url: str)
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
    