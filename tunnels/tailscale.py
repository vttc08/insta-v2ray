import subprocess
from helper.check import check_binary, is_docker, check_binary_status
from helper.error import binary_not_found, tunnel_url_not_found, tunnel_limits_exceeded, binary_nonzero_exit, localhost_warning
from configuration import tailscale_mode, bin_path
import logging
from tunnels.base import __BaseTunnel

logger = logging.getLogger(__name__)

# def prerequisites(self):
#     if running_in_docker or not check_binary("tailscale"):
#         error = binary_not_found("tailscale", self.__class__.__name__)
#         logger.error(error)
#         raise RuntimeError(error)
#     if not check_binary_status("tailscale funnel"):
#         error = binary_nonzero_exit("tailscale", self.__class__.__name__)
#         logger.error(error)
#         raise RuntimeError(error)

class __TailscaleCLI(__BaseTunnel):
    limit = 1
    tunnel_url_regex = r"https://[^\s]+\.ts.net"
    cmdline = f"tailscale funnel {{port}}"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
    
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