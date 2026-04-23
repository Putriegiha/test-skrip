from app import db

class Pengguna(db.Model):
    __tablename__ = 'PENGGUNA'
    ID_PENGGUNA = db.Column(db.Integer, primary_key=True)
    USERNAME = db.Column(db.String(50), nullable=False)
    EMAIL = db.Column(db.String(50), nullable=False)
    PASSWORD = db.Column(db.String(255), nullable=False)
    TANGGAL_DAFTAR = db.Column(db.Date)
    VEKTOR_PROFIL = db.Column(db.Text)
    IS_ONBOARDED = db.Column(db.SmallInteger, default=0)
