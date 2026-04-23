from app import create_app, db
from app.models.destinasi import DestinasiWisata
from app.models.pengguna import Pengguna
import datetime

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        # seed sample destinasi
        if DestinasiWisata.query.count() == 0:
            sample = [
                DestinasiWisata(ID_DESTINASI=1, KABUPATEN_KOTA='Malang', JENIS_WISATA='Alam', NAMA_DESTINASI='Pantai Balekambang', DESKRIPSI='Pantai indah di Malang', STATUS=1, RATING=4.5),
                DestinasiWisata(ID_DESTINASI=2, KABUPATEN_KOTA='Bangkalan', JENIS_WISATA='Budaya', NAMA_DESTINASI='Museum A', DESKRIPSI='Museum sejarah', STATUS=1, RATING=4.0),
            ]
            for d in sample:
                db.session.add(d)
        # seed sample user
        if Pengguna.query.count() == 0:
            u = Pengguna(ID_PENGGUNA=1, USERNAME='tester', EMAIL='test@example.com', PASSWORD='password', TANGGAL_DAFTAR=datetime.date.today())
            db.session.add(u)
        db.session.commit()
        print('DB initialized and seeded (SQLite dev).')

if __name__ == '__main__':
    init_db()
