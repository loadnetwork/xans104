"""High-level HuggingFace utilities."""

from __future__ import annotations

import tempfile
from typing import Any, Dict, Optional, Tuple, Type

from .remote import (
    DEFAULT_GATEWAY,
    extract_remote_dataitem_to_hf_dir
)


def load_model(
    dataitem_id: str,
    *,
    output_dir: Optional[str] = None,
    gateway_url: str = DEFAULT_GATEWAY,
    cache_path: Optional[str] = None,
    auth_token: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 60,
    model_cls: Optional[Type] = None,
    tokenizer_cls: Optional[Type] = None,
    model_kwargs: Optional[Dict[str, Any]] = None,
    tokenizer_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[Any, Any, str]:
    """Download & load a HuggingFace model directly from a DataItem ID.

    Returns a tuple of ``(tokenizer, model, model_dir)`` ready for inference.
    ``transformers`` must be installed in the calling environment.
    """

    model_dir = output_dir or tempfile.mkdtemp(prefix="xans104-hf-model-")

    extract_remote_dataitem_to_hf_dir(
        dataitem_id,
        model_dir,
        gateway_url=gateway_url,
        cache_path=cache_path,
        auth_token=auth_token,
        headers=headers,
        timeout=timeout,
    )

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "transformers must be installed to use xans104.load_model()"
        ) from exc

    tokenizer_factory = tokenizer_cls or AutoTokenizer
    model_factory = model_cls or AutoModelForCausalLM

    tokenizer = tokenizer_factory.from_pretrained(
        model_dir, **(tokenizer_kwargs or {})
    )
    model = model_factory.from_pretrained(model_dir, **(model_kwargs or {}))

    return tokenizer, model, model_dir
