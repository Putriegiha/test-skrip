from app import db

class PreferensiAwal(db.Model):
    __tablename__ = 'PREFERENSI_AWAL'
    ID_PREFERENSI = db.Column(db.Integer, primary_key=True)
    ID_PENGGUNA = db.Column(db.Integer, nullable=False)
    JENIS_WISATA = db.Column(db.String(100), nullable=False)
