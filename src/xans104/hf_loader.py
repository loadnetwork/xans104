import os
import shutil
import tarfile
from .dataitem import extract_payload, get_payload_offset_from_file, InvalidDataItem


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


def extract_dataitem_file_to_hf_dir(model_path: str, output_dir: str):
    """Extract a DataItem stored on disk into a HuggingFace-ready directory."""

    os.makedirs(output_dir, exist_ok=True)

    with open(model_path, "rb") as src:
        offset = get_payload_offset_from_file(src)
        magic = src.read(2)
        if len(magic) < 2:
            raise InvalidDataItem("payload is truncated; missing header bytes")

        src.seek(offset, os.SEEK_SET)

        if magic == b"\x1f\x8b":
            tar_path = os.path.join(output_dir, "model.tar.gz")
            _copy_stream_to_path(src, tar_path)
            with tarfile.open(tar_path) as tar:
                tar.extractall(output_dir)
            return output_dir

        raw_model_path = os.path.join(output_dir, "model.bin")
        _copy_stream_to_path(src, raw_model_path)
        return output_dir


def _copy_stream_to_path(stream, destination: str, chunk_size: int = 1024 * 1024):
    with open(destination, "wb") as dst:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            dst.write(chunk)
