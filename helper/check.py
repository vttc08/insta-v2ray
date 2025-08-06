import os
import subprocess
import re

def check_binary(path: str) -> bool:
    """
    Check if a binary exists at the specified path.
    """
    fullpath = subprocess.run(f"which {path}", shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    return os.path.isfile(fullpath) and os.access(fullpath, os.X_OK)

def check_all_binaries(bin_path: str, binary_name: str) -> str:
    """
    Check if a binary exists in the specified path or in the current directory.
    Returns the path if found, otherwise returns None.
    """
    paths = [
        os.path.realpath(os.path.join(bin_path, binary_name)),
        os.path.realpath(binary_name)
    ]
    for p in paths:
        if check_binary(p):
            return p
    return None

def is_docker() -> bool:
    """
    Check if the script is running inside a Docker container.
    """
    return os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')

def check_node_runtime() -> bool:
    """
    Check if Node.js is installed and accessible.
    """
    try:
        result = subprocess.run(['node', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_binary_status(cli_command: str, expected_output=None, unexpected_output=None) -> bool:
    """
    Check if a binary command succeeds and optionally match output using regex.
    """
    try:
        result = subprocess.run(cli_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return False
        if expected_output and not re.search(expected_output, result.stdout):
            return False
        if unexpected_output and re.search(unexpected_output, result.stdout):
            return False
        return True
    except Exception:
        return False