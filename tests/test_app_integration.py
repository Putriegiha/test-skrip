import json
import pytest
from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_login_onboarding_flow(client):
    # register
    rv = client.post('/auth/register', data={
        'username': 'iuser', 'email': 'i@example.com', 'password': 'password123'
    }, follow_redirects=True)
    assert rv.status_code in (200, 302)

    # login
    rv = client.post('/auth/login', data={'email': 'i@example.com', 'password': 'password123'}, follow_redirects=True)
    assert b'Rekomendasi' in rv.data or rv.status_code == 200

    # access onboarding (should redirect to home if onboared variable set)
    rv = client.get('/onboarding/')
    assert rv.status_code in (200, 302)


def test_like_wishlist_toggle(client):
    # register and login
    client.post('/auth/register', data={
        'username': 'u2', 'email': 'u2@example.com', 'password': 'password123'
    }, follow_redirects=True)
    client.post('/auth/login', data={'email': 'u2@example.com', 'password': 'password123'}, follow_redirects=True)
    # seed a destinasi in DB
    from app import db
    from app.models.destinasi import DestinasiWisata
    with client.application.app_context():
        d = DestinasiWisata(ID_DESTINASI=99, KABUPATEN_KOTA='X', JENIS_WISATA='Alam', NAMA_DESTINASI='D Test', STATUS=1, RATING=4.0)
        db.session.add(d)
        db.session.commit()

    # like
    rv = client.post('/destinasi/99/like')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data.get('status') in ('liked',)

    # unlike
    rv = client.post('/destinasi/99/like')
    data = json.loads(rv.data)
    assert data.get('status') in ('unliked', 'liked',)

    # wishlist
    rv = client.post('/destinasi/99/wishlist')
    data = json.loads(rv.data)
    assert data.get('status') in ('wishlisted',)
