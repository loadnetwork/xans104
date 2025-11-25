"""Helpers for storing HuggingFace snapshots on Load S3 as ANS-104 files."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import shutil
from importlib.metadata import version
from huggingface_hub import snapshot_download

DEFAULT_AGENT_URL = "https://load-s3-agent.load.network/upload"
__version__ = version("xans104")


def create_model_dataitem(
    repo_id: str,
    *,
    token: str,
    tags: dict[str, str] | None = None,
    agent_url: str = DEFAULT_AGENT_URL,
) -> str:
    """Download ``repo_id`` from HuggingFace and push it to Load S3."""

    normalized_tags = {"model": repo_id, "SDK": "xans104.py", "SDK-Version": __version__, "framework": "huggingface", **(tags or {})}

    tmp = tempfile.mkdtemp(prefix="xans104-hf-")
    try:
        model_dir = Path(tmp) / "snapshot"
        snapshot_download(repo_id=repo_id, local_dir=model_dir)

        tar_path = Path(tmp) / "model.tar.gz"
        subprocess.check_call(["tar", "-czf", str(tar_path), "-C", str(model_dir), "."])

        tag_payload = json.dumps([
            {"key": k, "value": v} for k, v in normalized_tags.items()
        ])

        response = subprocess.check_output(
            [
                "curl",
                "-sS",
                "-X",
                "POST",
                agent_url,
                "-H",
                f"Authorization: Bearer {token}",
                "-F",
                f"file=@{tar_path};type=application/gzip",
                "-F",
                "content_type=application/gzip",
                "-F",
                f"tags={tag_payload}",
            ],
            text=True,
        )

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return json.loads(response)["dataitem_id"]

