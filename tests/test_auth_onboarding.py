from app import db
from app.models.pengguna import Pengguna


def test_register_and_onboarding(client):
    # register
    rv = client.post('/auth/register', data={'username':'tuser','email':'t@example.com','password':'pass123'}, follow_redirects=True)
    assert rv.status_code in (200,302)

    # login
    rv = client.post('/auth/login', data={'email':'t@example.com','password':'pass123'}, follow_redirects=True)
    assert rv.status_code in (200,302)

    # verify user in DB
    with client.application.app_context():
        u = Pengguna.query.filter_by(EMAIL='t@example.com').first()
        assert u is not None
