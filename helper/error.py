def binary_not_found(binary_name: str, provider_name: str, **kwargs) -> str:
    """
    Returns an error message indicating that the specified binary was not found.
    """
    return f"{binary_name} binary not found or is not executable for {provider_name}. Please consult documentation to properly install or configure it. Additional arguments: {kwargs}" 

def binary_nonzero_exit(binary_name: str, provider_name: str, **kwargs) -> str:
    """
    Returns an error message indicating that the specified binary exited with a non-zero status.
    """
    return f"{binary_name} binary exited with non-zero status for {provider_name}. Please check the logs for more details. Additional arguments: {kwargs}"

def api_error_stopping_tunnel(e: str) -> str:
    """
    Returns an error message indicating that there was an API error while stopping the tunnel.
    """
    return f"Error stopping tunnel: {e}."

def tunnel_url_not_found(**kwargs) -> str:
    """
    Returns an error message indicating that the tunnel URL was not found.
    """
    return f"Tunnel URL not found. Details: {kwargs}."

def tunnel_limits_exceeded(provider_name: str, limit: int) -> str:
    """
    Returns an error message indicating that the tunnel limit has been exceeded for the specified provider.
    """
    return f"Tunnel limit exceeded for {provider_name}. Only {limit} tunnels can be started at a time."

localhost_warning = "This tunnel is only available on localhost. Please use SSH or other forwarding tools to forward the port to localhost."