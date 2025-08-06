import subprocess
import threading
import re

# class Test:
#     def __init__():
#         pass
#     def start_tunnel(self):
#         pass

class MockCloudflareTunnel:
    tunnels = 0
    def __init__(self, host: str, port: int, **provider_kwargs):
        self.host = host
        self.port = port
        self.provider_kwargs = provider_kwargs  # e.g., "--no-autoupdate", "--region" etc.
        self.process = None
        self.limit = 20 # only one tunnel at a time test
        MockCloudflareTunnel.tunnels += 1
        if MockCloudflareTunnel.tunnels > self.limit:
            raise RuntimeError("Only one tunnel can be started at a time.")

    def start_tunnel(self):
        mock_command = "python3 cloudflare.py"
        print(f"Starting tunnel for {self.host}:{self.port} with command: {mock_command}")
        self.process = subprocess.Popen(
            mock_command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        url = None
        def read_stdout():
            nonlocal url
            for line in self.process.stdout:
                print("[process]", line.strip())
                match = re.search(r"https://[^\s]+\.trycloudflare.com", line)
                if match:
                    url = match.group(0).replace("https://", "")  
                    print(f"Tunnel URL found: {url}")
                    break
        reader = threading.Thread(target=read_stdout)
        reader.start()
        reader.join(timeout=10)
        if not url:
            self.process.kill()
            raise RuntimeError("Tunnel URL not found in time")
        
        return (self.process, url)
    
    
    