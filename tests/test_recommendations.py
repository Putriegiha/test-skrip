import numpy as np
from app.services.vector_engine import cosine_similarity, get_top_n_recommendations


class MockItem:
    def __init__(self, id, vector):
        self.ID_DESTINASI = id
        self.VEKTOR_ITEM = vector.tolist()


def test_get_top_n_recommendations_basic():
    user_vec = np.array([1.0, 0.0, 0.0])
    items = [MockItem(1, np.array([1.0, 0.0, 0.0])), MockItem(2, np.array([0.0, 1.0, 0.0])), MockItem(3, np.array([0.9, 0.1, 0.0]))]
    # call function expecting it to accept list-like; adapt if function signature differs
    recs = get_top_n_recommendations(user_vec, items, top_n=2)
    ids = [r.ID_DESTINASI for r in recs]
    assert ids[0] == 1
    assert 3 in ids
