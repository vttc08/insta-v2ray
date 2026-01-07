import dotenv
import os
import hashlib
import logging

dotenv.load_dotenv()
# Development mode
mode = "dev" if os.getenv("MODE", "development").lower() in ("dev", "development","debug","test") else "prod"

# General
bin_path = os.getenv("BIN_PATH", "./bin")
if not os.path.exists(bin_path):
    os.mkdir(bin_path)

# Frontend
api_password = os.getenv("API_PASSWORD", "api")
subscription_password = os.getenv("SUBSCRIPTION_PASSWORD","")
if len(subscription_password) < 16:
    print("Insecure subscription password, must be at least 16 characters long, contain uppercase letters and digits.")
    subscription_password = hashlib.sha256(subscription_password.encode()).hexdigest()
    print("Using hashed subscription password:", subscription_password)
custom_frontend = os.getenv("CUSTOM_FRONTEND", "false").lower() in ("true", "1", "yes")

# Tunnel URLs
tunnel_urls_env = os.getenv("TUNNEL_URLS", "")
tunnel_urls = [url.strip() for url in tunnel_urls_env.split(",") if url.strip()] if tunnel_urls_env else []    

# Pinggy
pinggy_token = os.getenv("PINGGY_TOKEN", "qr")
pinggy_url = os.getenv("PINGGY_URL", "free.pinggy.io")
pinggy_premium = os.getenv("PINGGY_PREMIUM", "false").lower() in ("true", "1", "yes")
pinggy_args = os.getenv("PINGGY_ARGS","")

# Cloudflare
cloudflare_binary = os.getenv("CLOUDFLARED_BINARY", "cloudflared")
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/configure-tunnels/cloudflared-parameters/run-parameters/
cloudflare_extra_args = os.getenv("CLOUDFLARED_EXTRA_ARGS", "") # e.g. --region=us --protocol=quic

# Tailscale
tailscale_mode = os.getenv("TAILSCALE_MODE", None)  # None, "cli", "docker"

# Zrok
zrok_binary = os.getenv("ZROK_BINARY", "zrok")

# Localtunnel
localtunnel_binary = os.getenv("LOCAL_TUNNEL_BINARY", "lt")

# Logging configuration
class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logging():
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(CustomFormatter())
    fileHandler = logging.FileHandler("app.log")
    fileHandler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    ))
    logging.basicConfig(
        level=logging.INFO,
        handlers=[streamHandler, fileHandler]
    )
