# from .cloudflared import MockCloudflareTunnel
# from .cloudflaretunnel import CloudflareTunnel # real one
# from .cftunnel2 import NewCFTunnel # new version of Cloudflare Tunnel
# from .badtunnel import BadTunnel # for testing error handling
# from .pinggy import PinggyTunnel
from v2ray.v2ray import VLESS, VMESS
from dataclasses import dataclass, field
import subprocess
import time
from typing import Optional
from helper.subscription import add_subscription, remove_subscription
from configuration import mode
import importlib
import inspect
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

ignored_tunnels = ["MockCloudflareTunnel", "BadTunnel", "NewCFTunnel"] if mode == "prod" else []

providers = []
provider_dir = Path(__file__).parent
for provider_file in provider_dir.glob("*.py"):
    if provider_file.name == "__init__.py" or provider_file.name.startswith("_"):
        continue
    module_name = f"tunnels.{provider_file.stem}"
    try:
        module = importlib.import_module(module_name)
        logger.info(f"Loaded provider module: {module_name}")
    except ImportError as e:
        logger.error(f"Failed to load provider module {module_name}: {e}")
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and hasattr(obj, 'start_tunnel') and obj.__name__ not in ignored_tunnels and not obj.__name__.startswith("__"):
            providers.append(obj)
            logger.info(f"Registered provider: {obj.__name__}")
 
@dataclass
class Tunnel:
    url: str # URL of V2Ray format
    provider_instance: object  # Must have a .start(self) method
    v: Optional[VLESS | VMESS]= None

    public_url: Optional[str] = None
    process: Optional[subprocess.Popen] = None
    start_time: Optional[float] = None
    logs: list[str] = field(default_factory=list)     

    def __eq__(self, other):
        if isinstance(other, Tunnel):
            return self.url == other.url and self.provider_instance.__class__.__name__ == other.provider_instance.__class__.__name__
        return False

    def __post_init__(self):
        if self.url.startswith("vless://"):
            self.v = VLESS(self.url)
            self.v.parse(self.url)
            transport = self.v.all_params.get('type', 'tcp')[0] # by default as list ['ws']
        elif self.url.startswith("vmess://"):
            self.v = VMESS(self.url)
            self.v.parse(self.url)
            transport = self.v.all_params.get('net','tcp')
        else:
            raise NotImplementedError("Only VLESS and VMESS URLs are supported.")
        if transport not in ['ws','grpc']:
            raise ValueError(f"Unsupported transport type: {transport}. Only 'ws' and 'grpc' are supported.")
            
        host = self.v.host
        port = self.v.port
        self.provider_instance = self.provider_instance(host=host, port=port)
        self.provider_name = self.provider_instance.__class__.__name__

    def start(self):
        if self.provider_instance is None:
            raise ValueError("Provider instance is not set.")
        try:
            self.process, self.public_url = self.provider_instance.start_tunnel()
        except Exception as e:
            logger.error(f"Error starting tunnel with {self.provider_name}: {e}")
            self.get_logs()
            raise RuntimeError(e)
        self.start_time = time.time()
        self.old_url = self.url
        self.v.update(self.public_url, self.provider_name)
        self.url = self.v.url
        add_subscription(self)  # Add the new URL to subscriptions
        logger.info(f"{self.provider_name} tunnel started: {self.public_url}")

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            logger.info(f"{self.provider_name} tunnel stopped: {self.public_url}")
            self.provider_instance.tunnel_url = None
            self.url = self.old_url
            self.process = None
            self.public_url = None
            self.start_time = None
            remove_subscription(self)
        else:
            logger.warning(f"{self.provider_name} tunnel has no process to terminate.")
    
    def get_logs(self):
        prov_instance = self.provider_instance
        while not prov_instance.log_queue.empty():
            log_line = prov_instance.log_queue.get()
            if log_line is None:
                break
            self.logs.append(log_line)