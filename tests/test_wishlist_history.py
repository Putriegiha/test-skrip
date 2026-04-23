import json
from app import db
from app.models.destinasi import DestinasiWisata
from app.models.history import HistoryRekomendasi


def test_wishlist_and_history(client):
    # create user and login
    client.post('/auth/register', data={'username':'huser','email':'h@example.com','password':'pass123'}, follow_redirects=True)
    client.post('/auth/login', data={'email':'h@example.com','password':'pass123'}, follow_redirects=True)

    with client.application.app_context():
        db.session.query(DestinasiWisata).delete()
        db.session.query(HistoryRekomendasi).delete()
        d = DestinasiWisata(ID_DESTINASI=77, NAMA_DESTINASI='Gunung Test', KABUPATEN_KOTA='Hill', JENIS_WISATA='Alam', STATUS=1, RATING=4.2)
        db.session.add(d)
        db.session.commit()

    # add to wishlist
    rv = client.post('/destinasi/77/wishlist')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data.get('status') in ('wishlisted',)

    # check history logged when viewing detail
    client.get('/destinasi/77')
    with client.application.app_context():
        h = HistoryRekomendasi.query.filter_by(ID_DESTINASI=77).first()
        assert h is not None
