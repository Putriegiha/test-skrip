import pytest

from app import db
from app.models.destinasi import DestinasiWisata


@pytest.fixture(autouse=True)
def seed_destinasi(client):
    with client.application.app_context():
        db.session.query(DestinasiWisata).delete()
        d = DestinasiWisata(ID_DESTINASI=1, NAMA_DESTINASI='Pantai Demo', KABUPATEN_KOTA='DemoCity', JENIS_WISATA='Alam', STATUS=1, RATING=4.5)
        db.session.add(d)
        db.session.commit()
    yield


def test_search_index(client):
    # ensure search page loads and seeded item appears
    rv = client.get('/search')
    assert rv.status_code == 200
    assert b'Pantai Demo' in rv.data
