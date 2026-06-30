from __future__ import annotations

from typing import Any, Optional


def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {
        "code": 0,
        "message": message,
        "data": data,
    }


def fail(code: int, message: str, data: Optional[Any] = None) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": data,
    }
