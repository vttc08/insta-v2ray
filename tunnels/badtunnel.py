import queue
import subprocess
import threading
import re

class BadTunnel():
    def __init__(self, host: str, port: int, **provider_kwargs):
        self.host = host
        self.port = port
        self.provider_kwargs = provider_kwargs  # e.g., "--no-autoupdate", "--region" etc.
        self.process = None

        self.log_queue = queue.Queue() # Create a queue to store log lines
        self.log_thread = None
        self._url_found_event = threading.Event() # Event to signal when URL is found

    def start_tunnel(self):
        shell_script_content = "for i in {1..10}; do echo 'Please authorize before creating a tunnel.'; sleep 1; done"
        mock_command_list = ['/bin/bash', '-c', shell_script_content]
        print(f"Starting tunnel for {self.host}:{self.port} with command: {mock_command_list}")
        self.process = subprocess.Popen(
            mock_command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        url = None
        def read_stdout():
            nonlocal url
            for line in self.process.stdout:
                decoded_line = line.strip()
                self.log_queue.put(decoded_line) # Put the line into the queue

                print("[process]", line.strip())
                match = re.search(r"https://[^\s]+\.trycloudflare.com", line)
                if match:
                    url = match.group(0).replace("https://", "")  
                    print(f"Tunnel URL found: {url}")
                    break
        reader = threading.Thread(target=read_stdout)
        reader.start()
        reader.join(timeout=2)
        if not url:
            self.process.kill()
            self.log_queue.put(None)
            raise RuntimeError("Tunnel URL not found in time")
        
        return (self.process, url)
    