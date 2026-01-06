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
    
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List
import logging

class Validator(ABC):
    @abstractmethod
    def validate(self) -> Tuple[bool, str]:
        """
        Returns (is_valid, error message)
        """
        pass

class BinaryCheck(Validator):
    def __init__(self, bin_path: str, binary_path: str, binary_name: str):
        """
        bin_path: location of binaries
        binary_path: executable name or full path of a specific binary
        binary_name: name of the binary
        """
        self.bin_path = bin_path
        self.binary_path = binary_path
        self.binary_name = binary_name
        self.checked_binary = None
    
    def validate(self) -> Tuple[bool, str]:
        self.checked_binary = check_all_binaries(self.bin_path, self.binary_path)
        if not self.checked_binary:
            return False, f"Binary '{self.binary_name}' not found"
        return True, ""

class NodeRuntimeCheck(Validator):
    def validate(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(["node", "--version"], 
                                 capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False, "Node.js runtime not found or not working"
            
            return True, ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Node.js runtime not found"

class DockerCheck(Validator):
    def validate(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(["docker", "--version"], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False, "Docker not found or not working"
            
            # Check if Docker daemon is running
            result = subprocess.run(["docker", "info"], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False, "Docker daemon is not running"
            
            return True, ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Docker not found"

class CustomCheck(Validator):
    def __init__(self, function, *args, **kwargs):
        """
        function: custom function
        *arg, **kwargs: custom function arguments
        """
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def validate(self) -> Tuple[bool, str]:
        try:
            result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            return False, f"Custom function encountered an error, {e}"
        if not result:
            return False, f"Custom function check failed."
        return True, ""

def validate_provider(checks: List[Validator], module_name: str) -> Tuple[bool, dict]:
    """
    Validate a provider with multiple checks.
    
    Args:
        checks: List of validation checks to perform
        module_name: Module name for logging
    
    Returns:
        Tuple of (is_valid, context_dict)
    """
    logger = logging.getLogger(module_name)
    disabled = False
    context = {}
    
    for check in checks:
        is_valid, error_msg = check.validate()
        
        if not is_valid:
            logger.warning(f"{module_name}: {error_msg}")
            disabled = True
        
        # Store binary path if it's a binary check
        if isinstance(check, BinaryCheck) and check.checked_binary:
            context[f"{check.binary_name}_binary"] = check.checked_binary
    
    return not disabled, context
