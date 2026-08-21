"""Password hashing — ``hashlib.scrypt``, stdlib only, parameters in the hash.

**The rule the product states:** a password is ≥ 8 characters and there is no
other rule (R5, signed). That is a *structural* check and it lives server-side;
the Korean sentence a reader sees when it fails is the client's, from the design's
own copy — this module raises, it never phrases.

**Why scrypt and not a dependency.** ``hashlib.scrypt`` is in the standard
library, is memory-hard (the property that makes GPU cracking expensive), and
needs no wheel, no compiler and no version pin to audit. Argon2id is the modern
first choice, but it costs a C dependency for a workspace whose whole PII set is
one email address, and the parameter story below means moving to it later costs
one branch in :func:`verify` plus a login-time rehash — never a password reset
for every reader.

**The parameters, and why exactly these.** ``n=2**14, r=8, p=1`` — measured
~25 ms per hash on the development machine, and the largest ``n`` that fits
OpenSSL's default ``maxmem``: ``n=2**15`` needs 32 MB and raises "memory limit
exceeded" unless an explicit ``maxmem`` is passed. Sitting at the ceiling of the
default is deliberate — a parameter that only works because a private knob was
turned up is one deployment away from a login endpoint that raises.

**The upgrade path is the encoding.** A stored hash carries its own algorithm and
parameters::

    scrypt$n=16384,r=8,p=1$<salt b64>$<key b64>

so raising ``n`` (or swapping the algorithm) means: bump :data:`CURRENT`, and
:func:`needs_rehash` starts returning ``True`` for every hash minted under the old
parameters. The caller re-hashes at the next successful **login**, where the
plaintext is legitimately in hand and the request is already a write. Old hashes
keep verifying under their own recorded parameters until then, so nothing is
locked out and no reader is emailed about it.

Nothing here logs, and nothing here formats a password into a message: a
plaintext never persists, never reaches a log line and never reaches an error
body.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass

__all__ = [
    "CURRENT",
    "MIN_LENGTH",
    "ScryptParams",
    "hash_password",
    "needs_rehash",
    "verify",
]

#: R5, signed: ≥ 8 characters, and no other rule. No class requirement, no
#: maximum-that-is-really-a-truncation, no forbidden-character list.
MIN_LENGTH = 8


@dataclass(frozen=True)
class ScryptParams:
    """One generation of hashing cost. Recorded inside every hash it produces."""

    n: int = 2**14
    r: int = 8
    p: int = 1
    dklen: int = 32
    salt_bytes: int = 16

    @property
    def label(self) -> str:
        return f"n={self.n},r={self.r},p={self.p}"


#: The parameters new hashes are minted with. Bump this, never edit a stored hash.
CURRENT = ScryptParams()

_ALGORITHM = "scrypt"


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _derive(password: str, salt: bytes, params: ScryptParams) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=params.n,
        r=params.r,
        p=params.p,
        dklen=params.dklen,
    )


def hash_password(password: str, *, params: ScryptParams = CURRENT) -> str:
    """A fresh salted hash of ``password``. Raises on a password below the rule."""
    if len(password) < MIN_LENGTH:
        raise ValueError(f"password shorter than {MIN_LENGTH} characters")
    salt = os.urandom(params.salt_bytes)
    key = _derive(password, salt, params)
    return f"{_ALGORITHM}${params.label}${_b64(salt)}${_b64(key)}"


def _parse(encoded: str) -> tuple[ScryptParams, bytes, bytes] | None:
    """``None`` for anything this module did not mint — never an exception.

    A malformed or foreign hash must fail a *login*, not crash it: the caller is
    on the credential path, where every failure is the same uniform answer.
    """
    parts = encoded.split("$")
    if len(parts) != 4 or parts[0] != _ALGORITHM:
        return None
    try:
        values = dict(item.split("=", 1) for item in parts[1].split(","))
        params = ScryptParams(
            n=int(values["n"]), r=int(values["r"]), p=int(values["p"])
        )
        salt = base64.b64decode(parts[2], validate=True)
        key = base64.b64decode(parts[3], validate=True)
    except (KeyError, ValueError):
        return None
    return ScryptParams(params.n, params.r, params.p, len(key), len(salt)), salt, key


def verify(password: str, encoded: str) -> bool:
    """Constant-time check of ``password`` against a stored hash."""
    parsed = _parse(encoded)
    if parsed is None:
        return False
    params, salt, key = parsed
    return hmac.compare_digest(_derive(password, salt, params), key)


def needs_rehash(encoded: str, *, params: ScryptParams = CURRENT) -> bool:
    """Was this hash minted under weaker (or unknown) parameters than today's?"""
    parsed = _parse(encoded)
    if parsed is None:
        return True
    stored = parsed[0]
    return (stored.n, stored.r, stored.p, stored.dklen) != (
        params.n,
        params.r,
        params.p,
        params.dklen,
    )
