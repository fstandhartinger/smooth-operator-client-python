"""
Server management utilities for the Smooth Operator Agent Tools.
"""

import os
import platform
import zipfile
import shutil
from pathlib import Path
from typing import Optional


def get_server_installation_path() -> str:
    """
    Get the path where the server should be installed.
    
    Returns:
        The path to the server installation directory
    """
    if platform.system() == "Windows":
        base_dir = os.path.join(os.environ.get('APPDATA', ''), "SmoothOperator", "AgentToolsServer")
    else:
        # For non-Windows platforms, use a platform-appropriate location
        base_dir = os.path.join(os.path.expanduser("~"), ".smooth-operator", "agent-tools-server")
    
    # Create the directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    return base_dir


def extract_server_files(destination_dir: Optional[str] = None) -> str:
    """
    Extract the server files to the specified destination directory.
    
    Args:
        destination_dir: Destination directory for the server files.
                        If None, uses the default installation path.
    
    Returns:
        The path to the directory where the server files were extracted
    
    Raises:
        FileNotFoundError: When server files cannot be found
    """
    if destination_dir is None:
        destination_dir = get_server_installation_path()
    
    # Get the path to the server zip file in the package
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server_zip = os.path.join(package_dir, "smooth_operator_agent_tools", "server", "smooth-operator-server.zip")
    
    if not os.path.exists(server_zip):
        raise FileNotFoundError(
            f"Server package not found at {server_zip}. "
            "Make sure the package was installed correctly."
        )
    
    # Extract the zip file contents
    with zipfile.ZipFile(server_zip, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            # Skip directories
            if file_info.filename.endswith('/'):
                continue
            
            # Extract the file, creating directories as needed
            target_path = os.path.join(destination_dir, file_info.filename)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Extract the file, overwriting if exists
            with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                shutil.copyfileobj(source, target)
    
    return destination_dir


def is_server_installed() -> bool:
    """
    Check if the server is installed.
    
    Returns:
        True if the server is installed, False otherwise
    """
    installation_path = get_server_installation_path()
    server_exe = os.path.join(installation_path, "smooth-operator-server.exe")
    return os.path.exists(server_exe)


def get_server_executable_path() -> str:
    """
    Get the path to the server executable.
    
    Returns:
        The path to the server executable
    
    Raises:
        FileNotFoundError: When server executable cannot be found
    """
    installation_path = get_server_installation_path()
    server_exe = os.path.join(installation_path, "smooth-operator-server.exe")
    
    if not os.path.exists(server_exe):
        # Try to extract the server files
        extract_server_files(installation_path)
        
        # Check again
        if not os.path.exists(server_exe):
            raise FileNotFoundError(
                f"Server executable not found at {server_exe} and could not be extracted. "
                "Make sure the package was installed correctly."
            )
    
    return server_exe
