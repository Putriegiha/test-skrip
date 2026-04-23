from app import db

class HistoryRekomendasi(db.Model):
    __tablename__ = 'HISTORY_REKOMENDASI'
    ID_HISTORY = db.Column(db.Integer, primary_key=True)
    ID_DESTINASI = db.Column(db.Integer, nullable=False)
    ID_PENGGUNA = db.Column(db.Integer, nullable=False)
    SKOR_CBF = db.Column(db.Float, nullable=False)
    SKOR_KNN = db.Column(db.Float, nullable=False, default=0.0)
    SKOR_HYBRID = db.Column(db.Float, nullable=False, default=0.0)
    TANGGAL_REKOMENDASI = db.Column(db.DateTime)
    TIPE_INTERAKSI = db.Column(db.String(20))
    IS_INTERACTED = db.Column(db.SmallInteger, default=0)
