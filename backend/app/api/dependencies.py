import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(x_api_key: str | None = Security(_api_key_header)) -> None:
    """
    Enforce API key auth when the API_KEY environment variable is set.
    When API_KEY is absent the check is skipped (open / local-dev mode).
    """
    required = os.getenv("API_KEY")
    if required is None:
        return
    if x_api_key != required:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
