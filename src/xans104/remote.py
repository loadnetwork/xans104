"""Helpers for downloading ANS-104 payloads from Load S3 gateways."""

from __future__ import annotations

import os
import tempfile
from typing import Dict, Optional

import requests
from .hf_loader import extract_dataitem_file_to_hf_dir

DEFAULT_GATEWAY = "https://gateway.s3-node-1.load.network"


def _build_headers(auth_token: Optional[str], headers: Optional[Dict[str, str]]):
    final = dict(headers or {})
    if auth_token:
        final.setdefault("Authorization", f"Bearer {auth_token}")
    return final


def _format_gateway_url(gateway_url: str, dataitem_id: str, binary: bool = True) -> str:
    base = gateway_url.rstrip("/")
    if binary:
        return f"{base}/binary/{dataitem_id}"
    return f"{base}/resolve/{dataitem_id}"
    


def download_dataitem(
    dataitem_id: str,
    destination: str,
    *,
    gateway_url: str = DEFAULT_GATEWAY,
    auth_token: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    chunk_size: int = 1024 * 1024,
    timeout: int = 60,
) -> str:
    """Stream a DataItem from the Load gateway into ``destination``."""

    os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)

    resp = requests.get(
        _format_gateway_url(gateway_url, dataitem_id, True),
        stream=True,
        timeout=timeout,
        headers=_build_headers(auth_token, headers),
    )
    resp.raise_for_status()

    with open(destination, "wb") as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)

    return destination

def extract_remote_dataitem_to_hf_dir(
    dataitem_id: str,
    output_dir: str,
    *,
    gateway_url: str = DEFAULT_GATEWAY,
    cache_path: Optional[str] = None,
    auth_token: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 60,
):
    """Download a DataItem and unpack it into ``output_dir``."""

    cleanup = False
    download_target = cache_path
    if download_target is None:
        fd, tmp_path = tempfile.mkstemp(prefix="xans104-", suffix=".ans104")
        os.close(fd)
        download_target = tmp_path
        cleanup = True

    try:
        download_dataitem(
            dataitem_id,
            download_target,
            gateway_url=gateway_url,
            auth_token=auth_token,
            headers=headers,
            timeout=timeout,
        )
        return extract_dataitem_file_to_hf_dir(download_target, output_dir)
    finally:
        if cleanup and os.path.exists(download_target):
            os.remove(download_target)
