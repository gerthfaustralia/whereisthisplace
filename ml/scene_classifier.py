"""Scene classification stubs for the WhereIsThisPlace project."""

from typing import List, Tuple


def predict_topk(image_bytes: bytes, k: int) -> List[Tuple[str, float]]:
    """Return dummy top-k scene predictions.

    Args:
        image_bytes: Raw image data.
        k: Number of predictions to return.

    Returns:
        A list of scene label/confidence tuples. This is currently a
        placeholder implementation.
    """
    # Placeholder implementation until a real ML model is integrated
    return [("?", 0.33)]
