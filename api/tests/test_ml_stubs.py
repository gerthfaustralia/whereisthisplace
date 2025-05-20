import sys
from pathlib import Path

# Ensure the project root is on the path so we can import the ml package
ROOT = Path(__file__).resolve().parents[1].parent
sys.path.append(str(ROOT))

from ml import retrieval, scene_classifier


def test_retrieval_search_returns_placeholder():
    results = retrieval.search(b"data", k=1)
    assert isinstance(results, list)
    assert results == [(0.0, 0.0, 0.1)]


def test_scene_classifier_predict_topk_returns_placeholder():
    results = scene_classifier.predict_topk(b"data", k=1)
    assert isinstance(results, list)
    assert results == [("?", 0.33)]
