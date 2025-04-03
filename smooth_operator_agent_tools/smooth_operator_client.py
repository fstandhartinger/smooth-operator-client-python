"""
Main client for the Smooth Operator Agent Tools API.
"""

import os
import json
import time
import random
import shutil
import zipfile
import platform
import subprocess
import tempfile
import pkgutil # For reading package data
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, TypeVar, Type, cast, Type
import requests
from requests import Response, HTTPError
from datetime import datetime
import logging # Use logging instead of print for internal messages

# Set up basic logging
logger = logging.getLogger(__name__)
# Configure logging level and format if needed (e.g., logging.basicConfig(level=logging.INFO))
# By default, logger might not output anything unless configured by the application using the library.

# Import models for type hinting and deserialization
# Import directly from the models file to avoid circular dependencies
from .models.models import (
    BaseModel, ActionResponse, ScreenshotResponse, OverviewResponse,
    WindowDetailResponse, SimpleResponse # Add other models used directly if any
)
from .api_classes import (
    ScreenshotApi, # Keep these for initialization
    SystemApi,
    MouseApi,
    KeyboardApi,
    ChromeApi,
    AutomationApi,
    CodeApi
)

T = TypeVar('T') # Generic type variable used elsewhere
TResponse = TypeVar('TResponse') # Define TResponse for response type hinting


class SmoothOperatorClient:
    """Main client for the Smooth Operator Agent Tools API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Creates a new instance of the SmoothOperatorClient.
        
        Args:
            api_key: Optional API key for authentication. Most methods don't require an API Key,
                    but for some, especially the ones that use AI, you need to provide a 
                    Screengrasp.com API Key.
            base_url: Optional base URL of the API. By default the url is automatically determined
                     by calling start_server(), alternatively you can also just point to an already
                     running Server instance by providing its base url here.
        """
        self._base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key or "no_api_key_specified"}'
        })
        self._server_process = None
        
        # Initialize API categories
        self.screenshot = ScreenshotApi(self)
        self.system = SystemApi(self)
        self.mouse = MouseApi(self)
        self.keyboard = KeyboardApi(self)
        self.chrome = ChromeApi(self)
        self.automation = AutomationApi(self)
        self.code = CodeApi(self)
    
    def start_server(self) -> None:
        """
        Starts the Smooth Operator Agent Tools Server.
        
        Raises:
            ValueError: When server is already running or base URL is already set manually
            FileNotFoundError: When server files cannot be found
            RuntimeError: When server fails to start or report port
        """
        if self._base_url is not None:
            raise ValueError("Cannot start server when base URL has been already set.")

        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting server...")

        # Ensure server is installed and get the path
        installation_folder = self._ensure_server_installed() # Changed from _get_installation_folder

        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Installation check completed.")

        # Generate random port number filename
        random_num = random.randint(1000000, 100000000)
        port_number_filename = f"portnr_{random_num}.txt"
        port_number_filepath = os.path.join(installation_folder, port_number_filename)
        
        # Delete the port number file if it exists from a previous run
        if os.path.exists(port_number_filepath):
            os.remove(port_number_filepath)
        
        # Start the server process
        server_exe = "smooth-operator-server.exe"
        if platform.system() != "Windows":
            # For non-Windows platforms, we might need to use Wine or another approach
            # This is a placeholder for cross-platform support
            raise NotImplementedError(
                "Currently, the server executable only runs on Windows. "
                "Support for other platforms is planned for future releases."
            )
        
        server_path = os.path.join(installation_folder, server_exe)
        if not os.path.exists(server_path):
            raise FileNotFoundError(f"Server executable not found at {server_path}")
        
        args = [
            server_path,
            "/silent", # Match C# implementation
            "/close-with-parent-process",
            "/managed-by-lib", # Keep commented for now unless needed
            "/apikey=no_api_key_provided", # Keep commented for now unless needed
            f"/portnrfile={port_number_filename}"
        ]
        
        self._server_process = subprocess.Popen(
            args,
            cwd=installation_folder,
            stdout=subprocess.DEVNULL, # Redirect stdout to avoid potential blocking
            stderr=subprocess.DEVNULL, # Redirect stderr to avoid potential blocking
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0 # Match C# CreateNoWindow=true
        )
        
        if self._server_process is None:
            raise RuntimeError("Failed to start the server process.")

        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Server process initiated.")
        # Give the server process a moment to initialize before we start polling intensely
        time.sleep(1.0) # Reverted sleep back to 1.0 second
        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Proceeding with port file check.")

        # Wait for the port number file to be created
        max_wait_time_ms = 300000  # 5 min max wait
        waited_ms = 0
        while not os.path.exists(port_number_filepath) and waited_ms < max_wait_time_ms:
            time.sleep(0.1)
            waited_ms += 100
        
        if not os.path.exists(port_number_filepath):
            self.stop_server()
            raise RuntimeError("Server failed to report port number within the timeout period.")
        
        # Read the port number
        with open(port_number_filepath, 'r') as f:
            port_number = f.read().strip()
        
        self._base_url = f"http://localhost:{port_number}"
        os.remove(port_number_filepath)

        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Server reported back it is running at port {port_number}.")
        

        # Check if server is running
        waited_ms = 0
        while True:
            start_time = time.time()
            try:
                result = self._get_internal("/tools-api/ping", expected_type=str) # Provide expected_type=str
                # The server sends the response body including quotes for plain text
                if result == '"pong"':
                    break  # Server is ready for requests
            except Exception as e:
                # Log the specific exception during ping attempt
                logger.warning(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Ping failed: {type(e).__name__} - {e}")
                # Continue waiting, server might still be starting
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            waited_ms += elapsed_ms
            
            if waited_ms > max_wait_time_ms:
                raise RuntimeError("Server failed to become responsive within the timeout period.")
            
            time.sleep(0.500)
            waited_ms += 500
            
            if waited_ms > max_wait_time_ms:
                raise RuntimeError("Server failed to become responsive within the timeout period.")

        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Server ping successful, server is running.")

    def stop_server(self) -> None:
        """
        Stops the Smooth Operator Agent Tools Server if it was started by this client.
        """
        if self._server_process is not None and self._server_process.poll() is None:
            try:
                self._server_process.kill()
                self._server_process.wait(timeout=5)  # Wait up to 5 seconds for the process to exit
            except Exception:
                # Ignore errors when trying to kill the process
                pass
            finally:
                self._server_process = None
    
    # Internal method for making requests and handling responses/deserialization
    def _request_internal(self, method: str, endpoint: str, 
                          expected_type: Type[TResponse], 
                          data: Optional[Dict[str, Any]] = None) -> Optional[TResponse]:
        """
        Internal method to send HTTP requests and handle response deserialization.
        
        Args:
            method: HTTP method ('GET' or 'POST')
            endpoint: API endpoint
            
        Raises:
            ValueError: When base URL is not set
            requests.HTTPError: When the request fails
        """
        if not self._base_url:
            raise ValueError("Base URL is not set. You must call start_server() first, or provide a base_url in the constructor.")
        
        url = f"{self._base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'} if method == 'POST' else {}
        json_data = None
        if method == 'POST':
             json_data = {} if data is None else {k: v for k, v in data.items() if v is not None}

        try:
            if method == 'GET':
                response = self._session.get(url)
            elif method == 'POST':
                response = self._session.post(url, json=json_data, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # Handle expected plain text response (like ping)
            if expected_type == str:
                 # Cast to expected type TResponse, which is str in this case
                 return cast(TResponse, response.text) 

            # Handle expected JSON response and deserialize using the model's from_dict
            if response.headers.get('content-type') == 'application/json':
                try:
                    json_response = response.json()
                    # Use the from_dict factory method from the BaseModel
                    instance = expected_type.from_dict(json_response)
                    if instance is None:
                         logger.error(f"Failed to create {expected_type.__name__} from JSON for {endpoint}")
                    return instance
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for {endpoint}: {e}")
                    logger.error(f"Response text: {response.text[:500]}") # Log first 500 chars
                    return None # Or raise a custom error
                except Exception as e: # Catch errors during from_dict conversion
                     logger.error(f"Error deserializing response for {endpoint} into {expected_type.__name__}: {e}")
                     # Log the received JSON that caused the error
                     try:
                         logger.error(f"JSON received: {json.dumps(json_response, indent=2)}")
                     except NameError: # json_response might not be defined if JSONDecodeError happened first
                          logger.error(f"Response text causing error: {response.text[:500]}")
                     return None # Or raise a custom error
            else:
                 # If JSON was expected but not received
                 if issubclass(expected_type, BaseModel):
                      logger.error(f"Expected JSON for {endpoint} but received content type: {response.headers.get('content-type')}")
                      logger.error(f"Response text: {response.text[:500]}")
                      return None
                 else: # If another type was expected (e.g., bytes), handle here if necessary
                      logger.warning(f"Unexpected content type for {endpoint}: {response.headers.get('content-type')}")
                      # Attempt to cast or handle non-JSON response based on expected_type if needed
                      # For now, return None if not str or JSON BaseModel expected
                      return None


        except HTTPError as http_err:
            logger.error(f"HTTP error occurred for {endpoint}: {http_err}")
            # Try to get more details from the response body if possible
            error_details = http_err.response.text[:500]
            try:
                 error_json = http_err.response.json()
                 error_details = json.dumps(error_json, indent=2)
            except json.JSONDecodeError:
                 pass # Keep the raw text if it's not JSON
            logger.error(f"Response body: {error_details}")
            # Optionally, create a specific error model instance if the API provides structured errors
            return None # Or raise a custom error
        except Exception as err:
            logger.error(f"An unexpected error occurred for {endpoint}: {err}")
            return None # Or raise a custom error

    # Convenience methods calling the internal request handler
    def _get_internal(self, endpoint: str, expected_type: Type[TResponse]) -> Optional[TResponse]:
        return self._request_internal('GET', endpoint, expected_type)

    def _post_internal(self, endpoint: str, expected_type: Type[TResponse], data: Optional[Dict[str, Any]] = None) -> Optional[TResponse]:
        return self._request_internal('POST', endpoint, expected_type, data)

    def _get_installation_folder(self) -> str:
        """Gets the target installation folder path based on the OS."""
        if platform.system() == "Windows":
            return os.path.join(os.environ.get('APPDATA', ''), "SmoothOperator", "AgentToolsServer")
        else:
            # For non-Windows platforms, use a platform-appropriate location
            return os.path.join(os.path.expanduser("~"), ".smooth-operator", "agent-tools-server")

    def _get_appdata_dir(self) -> Path:
        """Gets the appropriate application data directory based on the OS."""
        system = platform.system()
        if system == "Windows":
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata)
            return Path.home() / "AppData" / "Roaming" # Fallback
        # Add other OS logic here if needed (macOS, Linux)
        # else:
        #     # Fallback for unsupported OS or if needed
        #     logger.warning(f"Unsupported OS {system} for standard AppData. Using fallback dir.")
        #     package_dir = Path(pkg_resources.resource_filename("smooth_operator_agent_tools", "")).parent
        #     fallback_dir = package_dir / ".smooth_operator_data"
        #     fallback_dir.mkdir(exist_ok=True)
        #     return fallback_dir
        # For now, stick to the original logic for non-windows:
        return Path(os.path.expanduser("~")) / ".smooth-operator" / "agent-tools-server"

    def _ensure_server_installed(self) -> str:
        """
        Ensures the server executable is installed in the correct location and is the correct version.
        Extracts files if necessary. Called by start_server().

        Returns:
            Path to the installation folder (as string)

        Raises:
            FileNotFoundError: If embedded server files cannot be found in the package.
            IOError: If file operations fail.
        """
        start_time = time.time()
        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Ensuring installation...")

        try:
            appdata_base = self._get_appdata_dir()
            # Use Path objects for consistency
            installation_folder_path = appdata_base / "SmoothOperator" / "AgentToolsServer"
            installed_version_path = installation_folder_path / "installedversion.txt"
            server_exe_path = installation_folder_path / "smooth-operator-server.exe" # Assuming windows for now

            logger.info(f"Target installation folder: {installation_folder_path}")

            # Ensure installation folder exists
            installation_folder_path.mkdir(parents=True, exist_ok=True)

            # --- Get Packaged Version ---
            try:
                # Use pkgutil.get_data which is generally preferred for accessing package data
                # Assumes 'installedversion.txt' is at the ROOT of the source distribution
                # MANIFEST.in should include it: `include installedversion.txt`
                packaged_version_bytes = pkgutil.get_data("smooth_operator_agent_tools", "installedversion.txt")
                if packaged_version_bytes is None:
                     # Fallback attempt if not directly in package dir (e.g., if in parent during development install -e)
                     try:
                         script_dir = Path(__file__).parent
                         version_file_path_dev = script_dir.parent / "installedversion.txt"
                         if version_file_path_dev.exists():
                             packaged_version_bytes = version_file_path_dev.read_bytes()
                         else:
                             raise FileNotFoundError # Trigger outer except block
                     except Exception:
                           raise FileNotFoundError("Packaged 'installedversion.txt' not found.")

                packaged_version_content = packaged_version_bytes.decode('utf-8').strip()
                logger.info(f"Packaged version: {packaged_version_content}")
            except Exception as e:
                logger.error(f"Error reading packaged version file: {e}", exc_info=True)
                raise FileNotFoundError("Could not read packaged server version. Ensure 'installedversion.txt' is included at the package root.") from e

            # --- Check Installed Version ---
            needs_extraction = True
            if installed_version_path.exists():
                try:
                    installed_version_content = installed_version_path.read_text(encoding='utf-8').strip()
                    logger.info(f"Found installed version: {installed_version_content}")
                    # Also check if the server executable exists, in case install was interrupted
                    if installed_version_content == packaged_version_content and server_exe_path.exists():
                        logger.info("Installed version matches packaged version and server executable exists. Skipping extraction.")
                        needs_extraction = False
                    elif installed_version_content != packaged_version_content:
                        logger.info(f"Installed version ({installed_version_content}) differs from packaged ({packaged_version_content}). Upgrading.")
                    else: # Versions match but exe missing
                         logger.info(f"Version matches but server executable missing at {server_exe_path}. Re-extracting.")
                except Exception as e:
                    logger.warning(f"Error reading installed version file ({installed_version_path}): {e}. Proceeding with extraction.")
            else:
                logger.info("No existing installation found. Proceeding with extraction.")

            # --- Extract if Needed ---
            if needs_extraction:
                logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting to extract server files...")
                try:
                    # Get packaged zip file content
                    zip_content_bytes = pkgutil.get_data("smooth_operator_agent_tools", "smooth-operator-server.zip")
                    if zip_content_bytes is None:
                        # Fallback attempt for development install -e
                         try:
                             script_dir = Path(__file__).parent
                             zip_file_path_dev = script_dir.parent / "smooth-operator-server.zip"
                             if zip_file_path_dev.exists():
                                 zip_content_bytes = zip_file_path_dev.read_bytes()
                             else:
                                 raise FileNotFoundError # Trigger outer except block
                         except Exception:
                              raise FileNotFoundError("Packaged 'smooth-operator-server.zip' not found.")


                    # Extract using temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
                        temp_zip.write(zip_content_bytes)
                        temp_zip_path = temp_zip.name

                    try:
                        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                            zip_ref.extractall(installation_folder_path)
                        logger.info(f"Extracted server files to {installation_folder_path}")
                    finally:
                        if os.path.exists(temp_zip_path):
                            os.remove(temp_zip_path)

                    # Write the new version file *after* successful extraction
                    installed_version_path.write_text(packaged_version_content, encoding='utf-8')
                    logger.info(f"Wrote version file {installed_version_path}")
                    logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Server files extracted successfully.")

                except FileNotFoundError as e:
                     logger.error(f"Error: {e}. Ensure 'smooth-operator-server.zip' is included at the package root.", exc_info=True)
                     raise # Re-raise critical error
                except Exception as e:
                    logger.error(f"An error occurred during extraction: {e}", exc_info=True)
                    # Don't write version file if extraction failed
                    raise IOError("Failed during server file extraction.") from e
            else:
                 logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Correct version already installed.")

            end_time = time.time()
            logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Installation ensured in {end_time - start_time:.2f} seconds.")

            return str(installation_folder_path) # Return as string as expected by start_server

        except Exception as e:
            # Catch any unexpected errors during the process
            logger.error(f"An unexpected error occurred during installation check: {e}", exc_info=True)
            # Depending on severity, might want to raise or just log
            raise # Re-raise unexpected errors

    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context manager."""
        self.close()
    
    def close(self):
        """Close the client and release resources."""
        self.stop_server()
        self._session.close()
    
    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup
