"""Common utilities."""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid4())


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.utcnow()


def hash_data(data: Dict[str, Any]) -> str:
    """Generate a hash for data content."""
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()


def safe_get(dictionary: Dict, *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary values."""
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result
