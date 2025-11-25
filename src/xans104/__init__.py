"""Public API surface for xANS-104 helpers."""

from importlib import metadata

from .hf_integration import load_model
from .storage import create_model_dataitem

try:  
    __version__ = metadata.version("xans104")
except metadata.PackageNotFoundError:
    __version__ = "0.1.0"


__all__ = [
    "__version__",
    "load_model",
    "create_model_dataitem"
]
