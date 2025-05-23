from ml import retrieval, scene_classifier, fuse


def test_retrieval_search_returns_placeholder():
    results = retrieval.search(b"data", k=1)
    assert isinstance(results, list)
    assert results == [(0.0, 0.0, 0.1)]


def test_scene_classifier_predict_topk_returns_placeholder():
    results = scene_classifier.predict_topk(b"data", k=1)
    assert isinstance(results, list)
    assert results == [("?", 0.33)]


def test_fuse_returns_first_retrieval():
    location, confidence = fuse.fuse(
        scene=[("urban", 0.9)],
        retrieval=[(1.0, 2.0, 0.8)],
    )
    assert location == (1.0, 2.0)
    assert confidence == 0.8
