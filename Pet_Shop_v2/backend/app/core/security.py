import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Optional

from .config import settings
from .exceptions import UnauthorizedError


PASSWORD_HASH_NAME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 200_000


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return "$".join(
        [
            PASSWORD_HASH_NAME,
            str(PASSWORD_ITERATIONS),
            _b64_encode(salt),
            _b64_encode(digest),
        ]
    )


def verify_password(password: str, password_hash: Optional[str]) -> bool:
    if not password_hash:
        return False

    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
        if algorithm != PASSWORD_HASH_NAME:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            _b64_decode(salt),
            int(iterations),
        )
        return hmac.compare_digest(_b64_encode(digest), expected)
    except (ValueError, TypeError):
        return False


def _sign(signing_input: str) -> str:
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _b64_encode(signature)


def create_access_token(
    subject: str,
    claims: Optional[dict[str, Any]] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    now = int(time.time())
    expires_in = (expires_minutes or settings.access_token_expire_minutes) * 60
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_in,
        "typ": "access",
    }
    if claims:
        payload.update(claims)

    header_segment = _b64_encode(
        json.dumps(
            {"alg": "HS256", "typ": "JWT"},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    payload_segment = _b64_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signing_input = f"{header_segment}.{payload_segment}"
    return f"{signing_input}.{_sign(signing_input)}"


def parse_access_token(token: str) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature = token.split(".", 2)
    except ValueError as exc:
        raise UnauthorizedError("Invalid token") from exc

    expected_signature = _sign(f"{header_segment}.{payload_segment}")
    if not hmac.compare_digest(signature, expected_signature):
        raise UnauthorizedError("Invalid token")

    try:
        header = json.loads(_b64_decode(header_segment).decode("utf-8"))
        payload = json.loads(_b64_decode(payload_segment).decode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise UnauthorizedError("Invalid token") from exc

    if header.get("alg") != "HS256" or header.get("typ") != "JWT":
        raise UnauthorizedError("Invalid token header")

    if payload.get("typ") != "access":
        raise UnauthorizedError("Invalid token type")

    expires_at = int(payload.get("exp", 0))
    if expires_at < int(time.time()):
        raise UnauthorizedError("Token expired")

    return payload


def protect_sensitive_value(value: str) -> str:
    digest = hmac.new(
        settings.secret_key.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"hmac_sha256${digest}"
