"""
Smooth Operator Agent Tools - Python Library

A Python client library for the Smooth Operator Agent Tools.
"""

__version__ = "0.1.0" # Placeholder, update as needed

# Import the main client class
from .smooth_operator_client import SmoothOperatorClient

# Define __all__ for the top-level package
# Only export the client class from the top level
__all__ = [
    'SmoothOperatorClient'
]
