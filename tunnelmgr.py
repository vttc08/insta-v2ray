import logging
logger = logging.getLogger(__name__)

from configuration import tunnel_urls
from tunnels import providers, Tunnel


tunnels = tunnel_urls
tun_tasks = []

def prepare_tunnels():
    for tunnel in tunnels:
        for provider in providers:
            try:
                tunnel_instance = Tunnel(
                    url=tunnel,
                    provider_instance=provider
                )
            except Exception as e:
                continue
            tun_tasks.append(tunnel_instance)

def reset_one_tunnel(tunnel: Tunnel):
    """
    Reset a single tunnel
    """
    try:
        tunnel.stop()
    except Exception as e:
        logger.error(f"Error stopping tunnel: {e}")
    try:
        tunnel.start()
    except Exception as e:
        logger.error(f"Error starting tunnel: {e}")

def stop_one_tunnel(tunnel: Tunnel):
    try:
        tunnel.stop()
    except Exception as e:
        raise RuntimeError(str(e))