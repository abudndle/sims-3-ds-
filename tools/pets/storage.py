"""Isolated Pets sidecar storage; never opens or modifies retail .sav files.

Caller selects a dedicated .pets.json file. Atomic writes include an integrity
checksum. This is a host-side prototype, NOT an in-ROM save implementation.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .model import HouseholdPets, PetError

MAGIC = "sims3-ds-pets-sidecar"
VERSION = 1
MAX_BYTES = 65536


def _check_path(path):
    path = Path(path)
    if path.suffix.lower() != ".json" or not path.name.endswith(".pets.json"):
        raise PetError("sidecar path must end with .pets.json")
    return path


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def encode(household):
    if not isinstance(household, HouseholdPets):
        raise PetError("expected HouseholdPets")
    payload = household.to_dict()
    HouseholdPets.from_dict(payload)
    digest = hashlib.sha256(_canonical(payload)).hexdigest()
    data = _canonical({"magic": MAGIC, "format_version": VERSION, "pets": payload, "sha256": digest})
    if len(data) > MAX_BYTES:
        raise PetError("pets sidecar exceeds maximum size")
    return data + b"\n"


def decode(data):
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise PetError("invalid or oversized sidecar")
    try:
        envelope = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise PetError("invalid sidecar JSON") from exc
    if not isinstance(envelope, dict) or set(envelope) != {"magic", "format_version", "pets", "sha256"}:
        raise PetError("invalid sidecar envelope")
    if envelope["magic"] != MAGIC or type(envelope["format_version"]) is not int or envelope["format_version"] != VERSION:
        raise PetError("unsupported sidecar version")
    digest = envelope["sha256"]
    if not isinstance(digest, str) or len(digest) != 64:
        raise PetError("invalid sidecar checksum")
    try:
        expected = hashlib.sha256(_canonical(envelope["pets"])).hexdigest()
    except (TypeError, ValueError) as exc:
        raise PetError("invalid sidecar data") from exc
    if digest != expected:
        raise PetError("pets sidecar integrity check failed")
    return HouseholdPets.from_dict(envelope["pets"])


def save_sidecar(path, household):
    """Atomically replace ONLY the designated pets sidecar."""
    path = _check_path(path)
    encoded = encode(household)
    directory = path.parent
    if not directory.is_dir():
        raise PetError("sidecar directory does not exist")
    if path.is_symlink():
        raise PetError("sidecar path may not be a symlink")
    fd, temporary = tempfile.mkstemp(prefix=".pets-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_sidecar(path):
    path = _check_path(path)
    if path.is_symlink():
        raise PetError("sidecar path may not be a symlink")
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    return decode(raw)
