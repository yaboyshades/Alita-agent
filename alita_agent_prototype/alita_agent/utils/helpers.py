"""General utility functions for the Alita Agent Framework."""

import uuid
from datetime import datetime


def generate_unique_id(prefix: str = "item") -> str:
    """Generates a unique ID with a timestamp and random component."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}_{uuid.uuid4().hex[:6]}"
