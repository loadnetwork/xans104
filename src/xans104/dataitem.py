# translated from https://github.com/loadnetwork/load_hb/blob/s3-node-1/native/s3_nif/src/sidecar/ans104.rs

import io
import os
import struct
from typing import BinaryIO


# Signature + owner byte sizes
ARWEAVE_SIG_BYTES = 512
ARWEAVE_OWNER_BYTES = 512

SOL_SIG_BYTES = 64
SOL_OWNER_BYTES = 32

ETH_SIG_BYTES = 65
ETH_OWNER_BYTES = 65


class SignatureType:
    ARWEAVE = 1
    ED25519 = 2
    ETHEREUM = 3

    @staticmethod
    def from_u16(v: int):
        return {
            1: SignatureType.ARWEAVE,
            2: SignatureType.ED25519,
            3: SignatureType.ETHEREUM,
        }.get(v)

    @staticmethod
    def byte_values(sig_type: int) -> int:
        if sig_type == SignatureType.ARWEAVE:
            return ARWEAVE_SIG_BYTES + ARWEAVE_OWNER_BYTES
        if sig_type == SignatureType.ED25519:
            return SOL_SIG_BYTES + SOL_OWNER_BYTES
        if sig_type == SignatureType.ETHEREUM:
            return ETH_SIG_BYTES + ETH_OWNER_BYTES
        raise ValueError(f"unknown signature type: {sig_type}")


class InvalidDataItem(ValueError):
    """Raised when an ANS-104 blob is malformed."""


def _read_exact(stream: BinaryIO, size: int, err: str) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        raise InvalidDataItem(err)
    return data


def _skip_bytes(stream: BinaryIO, amount: int, err: str):
    remaining = amount
    chunk = 64 * 1024
    while remaining > 0:
        piece = stream.read(min(remaining, chunk))
        if not piece:
            raise InvalidDataItem(err)
        remaining -= len(piece)


def _payload_offset_from_stream(stream: BinaryIO) -> int:
    cursor = 0

    sig_raw = _read_exact(stream, 2, "invalid ANS-104 signature header")
    sig_type, = struct.unpack("<H", sig_raw)
    cursor += 2

    di_type = SignatureType.from_u16(sig_type)
    if di_type is None:
        raise InvalidDataItem(f"invalid ANS-104 signature type: {sig_type}")

    sig_owner_bytes = SignatureType.byte_values(di_type)
    _skip_bytes(stream, sig_owner_bytes, "truncated signature/owner block")
    cursor += sig_owner_bytes

    cursor += _skip_optional_field(stream, "truncated target flag")
    cursor += _skip_optional_field(stream, "truncated anchor flag")

    tags_header = _read_exact(stream, 16, "truncated ANS-104 tags header")
    _, tag_bytes_len = struct.unpack("<QQ", tags_header)
    cursor += 16

    _skip_bytes(stream, tag_bytes_len, "invalid tag size in ANS-104 header")
    cursor += tag_bytes_len

    return cursor


def _skip_optional_field(stream: BinaryIO, err: str) -> int:
    flag = _read_exact(stream, 1, err)
    skipped = 1
    if flag == b"\x01":
        _skip_bytes(stream, 32, err)
        skipped += 32
    elif flag != b"\x00":
        raise InvalidDataItem("invalid optional field flag; expected 0 or 1")
    return skipped


def get_payload_offset(blob: bytes) -> int:
    """Return payload offset for an in-memory ANS-104 blob."""
    return _payload_offset_from_stream(io.BytesIO(blob))


def get_payload_offset_from_file(file_obj: BinaryIO) -> int:
    """Return payload offset and seek the file to the start of the payload."""
    if not file_obj.seekable():
        raise ValueError("file_obj must be seekable to compute payload offset")
    file_obj.seek(0, os.SEEK_SET)
    offset = _payload_offset_from_stream(file_obj)
    file_obj.seek(offset, os.SEEK_SET)
    return offset


def extract_payload(blob: bytes) -> bytes:
    offset = get_payload_offset(blob)
    return blob[offset:]
