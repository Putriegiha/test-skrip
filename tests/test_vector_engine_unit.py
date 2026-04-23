import numpy as np
from app.services import vector_engine


def test_cosine_similarity_identical():
    v = [1.0, 0.0, 0.0]
    assert vector_engine.cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    assert vector_engine.cosine_similarity(v1, v2) == pytest.approx(0.0)


def test_update_user_profile_moves_towards_item():
    u = np.array([0.0, 0.0])
    item = np.array([1.0, 0.0])
    new_u = vector_engine.update_user_profile(u, item, alpha=0.5)
    # centroid should move toward item
    assert new_u[0] > u[0]
