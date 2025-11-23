# translated from https://github.com/loadnetwork/load_hb/blob/s3-node-1/native/s3_nif/src/sidecar/ans104.rs

import struct


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


def get_payload_offset(blob: bytes) -> int:
    cursor = 0

    # u16 signature type
    sig_type, = struct.unpack_from("<H", blob, cursor)
    cursor += 2

    di_type = SignatureType.from_u16(sig_type)
    if di_type is None:
        raise ValueError(f"invalid ANS-104 signature type: {sig_type}")

    # skip signature + owner
    cursor += SignatureType.byte_values(di_type)

    # target
    if blob[cursor] == 1:
        cursor += 1 + 32
    else:
        cursor += 1

    # anchor
    if blob[cursor] == 1:
        cursor += 1 + 32
    else:
        cursor += 1

    # tags
    _, tag_bytes_len = struct.unpack_from("<QQ", blob, cursor)
    cursor += 16

    tag_end = cursor + tag_bytes_len
    if tag_end > len(blob):
        raise ValueError("invalid tag size in ANS-104 header")

    return tag_end


def extract_payload(blob: bytes) -> bytes:
    offset = get_payload_offset(blob)
    return blob[offset:]
