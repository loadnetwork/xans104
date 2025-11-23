import os
import tarfile
from .dataitem import extract_payload


def extract_dataitem_to_hf_dir(blob: bytes, output_dir: str):
    """
    Extract ANS-104 data field into a HuggingFace-compatible
    model directory.

    If the payload is a .tar.gz, it's extracted.
    Otherwise written raw.
    """
    os.makedirs(output_dir, exist_ok=True)

    payload = extract_payload(blob)

    # detect tarball
    if payload[:2] == b"\x1f\x8b":  # gzip header
        tar_path = os.path.join(output_dir, "model.tar.gz")
        with open(tar_path, "wb") as f:
            f.write(payload)

        with tarfile.open(tar_path) as tar:
            tar.extractall(output_dir)

        return output_dir

    # otherwise write raw payload
    model_path = os.path.join(output_dir, "model.bin")
    with open(model_path, "wb") as f:
        f.write(payload)

    return output_dir
