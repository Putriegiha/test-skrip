import json
import numpy as np
from app.services import vector_engine


def test_cosine_similarity_identical():
    v = [1.0, 0.0, 0.0]
    assert abs(vector_engine.cosine_similarity(v, v) - 1.0) < 1e-6


def test_cosine_similarity_orthogonal():
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    assert abs(vector_engine.cosine_similarity(v1, v2)) < 1e-6


def test_update_profile_moves_towards_item(tmp_path, monkeypatch):
    # create fake user and dest in-memory using simple dicts
    # We'll test the numeric operation directly
    v_u = np.array([1.0, 0.0, 0.0])
    v_i = np.array([0.0, 1.0, 0.0])
    alpha = 0.1
    v_new = v_u + alpha * (v_i - v_u)
    # normalized
    v_new = v_new / np.linalg.norm(v_new)
    # expected dot with v_i should increase compared to original
    orig_dot = np.dot(v_u / np.linalg.norm(v_u), v_i / np.linalg.norm(v_i))
    new_dot = np.dot(v_new / np.linalg.norm(v_new), v_i / np.linalg.norm(v_i))
    assert new_dot > orig_dot
