"""Image retrieval stubs for the WhereIsThisPlace project."""

from typing import List, Tuple


def search(image_bytes: bytes, k: int) -> List[Tuple[float, float, float]]:
    """Return dummy nearest-neighbor search results.

    Args:
        image_bytes: Raw image data for the query image.
        k: Number of neighbors to return.

    Returns:
        A list of (latitude, longitude, score) tuples. This is currently a
        placeholder implementation.
    """
    # Placeholder implementation until a real retrieval model is integrated
    return [(0.0, 0.0, 0.1)]
