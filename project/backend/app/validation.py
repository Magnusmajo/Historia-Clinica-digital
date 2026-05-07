from typing import Any

from fastapi import HTTPException, status

CONTROL_CHARACTERS = {chr(index) for index in range(32)} - {"\n", "\r", "\t"}


def sanitize_text(value: str | None, *, max_length: int | None = None) -> str | None:
    if value is None:
        return None
    cleaned = "".join(char for char in str(value).strip() if char not in CONTROL_CHARACTERS)
    if not cleaned:
        return None
    if max_length is not None and len(cleaned) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"El texto supera el limite de {max_length} caracteres",
        )
    return cleaned


def sanitize_json(value: Any, *, max_string_length: int = 4000, max_depth: int = 6) -> Any:
    if max_depth < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="La estructura enviada es demasiado profunda",
        )
    if isinstance(value, str):
        return sanitize_text(value, max_length=max_string_length) or ""
    if isinstance(value, list):
        return [
            sanitize_json(item, max_string_length=max_string_length, max_depth=max_depth - 1)
            for item in value
        ]
    if isinstance(value, dict):
        return {
            str(sanitize_text(key, max_length=160) or ""): sanitize_json(
                item,
                max_string_length=max_string_length,
                max_depth=max_depth - 1,
            )
            for key, item in value.items()
        }
    return value
