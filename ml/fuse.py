"""Fusion utilities for the WhereIsThisPlace project."""

from typing import List, Tuple, Optional


def fuse(
    scene: List[Tuple[str, float]],
    retrieval: List[Tuple[float, float, float]],
    exif: Optional[dict] = None,
) -> Tuple[Tuple[float, float], float]:
    """Combine different signals to determine the final location.

    Currently this stub simply returns the first retrieval result and its
    confidence score.

    Args:
        scene: Scene classifier output (unused).
        retrieval: List of retrieval results as ``(lat, lon, score)`` tuples.
        exif: Optional EXIF metadata (unused).

    Returns:
        A tuple ``((lat, lon), confidence)``.
    """
    if not retrieval:
        raise ValueError("retrieval results cannot be empty")

    lat, lon, score = retrieval[0]
    return (lat, lon), float(score)
