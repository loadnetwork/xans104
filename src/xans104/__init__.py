"""Public API surface for xANS-104 helpers."""

from importlib import metadata

from .hf_integration import load_model
from .remote import DEFAULT_GATEWAY
# from .sagemaker import extract_dataitem_to_sagemaker_model_dir


try:  
    __version__ = metadata.version("xans104")
except metadata.PackageNotFoundError:
    __version__ = "0.1.0"


__all__ = [
    "__version__",
    "DEFAULT_GATEWAY",
    # "extract_dataitem_to_sagemaker_model_dir",
    "load_model",
]
