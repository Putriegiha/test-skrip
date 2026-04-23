from flask import Blueprint, render_template, session, redirect, url_for
from app.utils import login_required
from app.models.history import HistoryRekomendasi
from app.models.destinasi import DestinasiWisata

bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')


@bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    rows = HistoryRekomendasi.query.filter_by(ID_PENGGUNA=user_id, TIPE_INTERAKSI='wishlist', IS_INTERACTED=1).order_by(HistoryRekomendasi.TANGGAL_REKOMENDASI.desc()).all()
    dest_ids = [r.ID_DESTINASI for r in rows]
    destinasi = DestinasiWisata.query.filter(DestinasiWisata.ID_DESTINASI.in_(dest_ids)).all() if dest_ids else []
    return render_template('wishlist.html', destinasi=destinasi)
