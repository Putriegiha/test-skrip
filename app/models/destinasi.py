from app import db

class DestinasiWisata(db.Model):
    __tablename__ = 'DESTINASI_WISATA'
    ID_DESTINASI = db.Column(db.Integer, primary_key=True)
    KABUPATEN_KOTA = db.Column(db.String(100), nullable=False)
    JENIS_WISATA = db.Column(db.String(100), nullable=False)
    NAMA_DESTINASI = db.Column(db.String(100), nullable=False)
    DESKRIPSI = db.Column(db.Text)
    ALAMAT = db.Column(db.Text)
    RATING = db.Column(db.Float)
    TOTAL_RATING = db.Column(db.Integer)
    TITIK_KOORDINAT = db.Column(db.Float)
    STATUS = db.Column(db.SmallInteger)
    VEKTOR_ITEM = db.Column(db.Text)
