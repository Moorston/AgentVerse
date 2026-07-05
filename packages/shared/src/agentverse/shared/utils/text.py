"""Text processing utilities."""


def truncate(text: str, max_length: int = 1000) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."

def slugify(text: str) -> str:
    """Convert text to a simple slug."""
    return text.lower().replace(" ", "-").replace("/", "-")