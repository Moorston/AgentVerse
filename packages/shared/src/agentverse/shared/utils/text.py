"""Text processing utilities."""

import re
import unicodedata


def truncate(text: str, max_length: int = 1000) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."

def slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    - Normalizes Unicode characters (é → e, ñ → n)
    - Lowercases
    - Replaces whitespace and separators with hyphens
    - Removes non-alphanumeric characters (except hyphens)
    - Collapses consecutive hyphens
    - Strips leading and trailing hyphens
    """
    # Normalize Unicode (NFKD decomposes accented chars)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    text = text.lower()
    # Replace whitespace and common separators with hyphens
    text = re.sub(r"[\s/_]+", "-", text)
    # Remove characters that are not alphanumeric, hyphens, or dots
    text = re.sub(r"[^a-z0-9\-.]", "", text)
    # Collapse consecutive hyphens
    text = re.sub(r"-{2,}", "-", text)
    # Strip leading/trailing hyphens and dots
    text = text.strip("-.")
    return text