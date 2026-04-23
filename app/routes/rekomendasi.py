from flask import Blueprint, render_template, session, redirect, url_for
from app.utils import login_required
from datetime import datetime
from app.services.vector_engine import get_top_n_recommendations
from app.services.cache_service import cache
from app import db
from app.models.history import HistoryRekomendasi
from flask import request, jsonify
from app.services.vector_engine import update_user_profile

bp = Blueprint('rekomendasi', __name__)


@bp.route('/')
@login_required
def home():
    user_id = session.get('user_id')
    scored = get_top_n_recommendations(user_id, n=10)
    # Try cache first
    cache_key = f"reco:user:{user_id}:topn"
    cached = cache.get(cache_key)
    if cached:
        destinations = []
        from app.models.destinasi import DestinasiWisata
        for did in cached:
            d = DestinasiWisata.query.get(did)
            if d:
                destinations.append(d)
        return render_template('home.html', destinations=destinations)

    # Log to history
    for dest, skor in scored:
        h = HistoryRekomendasi(ID_DESTINASI=dest.ID_DESTINASI, ID_PENGGUNA=user_id,
                               SKOR_CBF=skor, SKOR_KNN=0.0, SKOR_HYBRID=skor,
                               TANGGAL_REKOMENDASI=datetime.utcnow())
        db.session.add(h)
    db.session.commit()
    destinations = [d for d, s in scored]
    # cache list of destination ids
    try:
        cache.set(cache_key, [d.ID_DESTINASI for d in destinations], ttl=300)
    except Exception:
        pass
    return render_template('home.html', destinations=destinations)


@bp.route('/destinasi/<int:id_destinasi>')
@login_required
def detail(id_destinasi):
    from app.models.destinasi import DestinasiWisata
    dest = DestinasiWisata.query.get(id_destinasi)
    if not dest:
        return redirect(url_for('rekomendasi.home'))
    return render_template('detail.html', dest=dest)


@bp.route('/destinasi/<int:id_destinasi>/like', methods=['POST'])
def like(id_destinasi):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'not_authenticated'}), 401
    # find existing history record for this user+dest with tipe_interaksi 'like'
    h = HistoryRekomendasi.query.filter_by(ID_PENGGUNA=user_id, ID_DESTINASI=id_destinasi, TIPE_INTERAKSI='like').order_by(HistoryRekomendasi.ID_HISTORY.desc()).first()
    if h and h.IS_INTERACTED == 1:
        # unlike
        h.IS_INTERACTED = 0
        db.session.commit()
        return jsonify({'status': 'unliked', 'success': True})
    else:
        # create or update
        if not h:
            h = HistoryRekomendasi(ID_DESTINASI=id_destinasi, ID_PENGGUNA=user_id, SKOR_CBF=0.0, SKOR_KNN=0.0, SKOR_HYBRID=0.0, TANGGAL_REKOMENDASI=datetime.utcnow(), TIPE_INTERAKSI='like', IS_INTERACTED=1)
            db.session.add(h)
        else:
            h.IS_INTERACTED = 1
            h.TIPE_INTERAKSI = 'like'
            h.TANGGAL_REKOMENDASI = datetime.utcnow()
        db.session.commit()
        # update profile with alpha for like
        update_user_profile(user_id, id_destinasi, alpha=0.10)
        # invalidate cache for this user
        try:
            cache.delete(f"reco:user:{user_id}:topn")
        except Exception:
            pass
        return jsonify({'status': 'liked', 'success': True})


@bp.route('/destinasi/<int:id_destinasi>/wishlist', methods=['POST'])
def wishlist_toggle(id_destinasi):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'not_authenticated'}), 401
    h = HistoryRekomendasi.query.filter_by(ID_PENGGUNA=user_id, ID_DESTINASI=id_destinasi, TIPE_INTERAKSI='wishlist').order_by(HistoryRekomendasi.ID_HISTORY.desc()).first()
    if h and h.IS_INTERACTED == 1:
        h.IS_INTERACTED = 0
        db.session.commit()
        return jsonify({'status': 'removed', 'success': True})
    else:
        if not h:
            h = HistoryRekomendasi(ID_DESTINASI=id_destinasi, ID_PENGGUNA=user_id, SKOR_CBF=0.0, SKOR_KNN=0.0, SKOR_HYBRID=0.0, TANGGAL_REKOMENDASI=datetime.utcnow(), TIPE_INTERAKSI='wishlist', IS_INTERACTED=1)
            db.session.add(h)
        else:
            h.IS_INTERACTED = 1
            h.TIPE_INTERAKSI = 'wishlist'
            h.TANGGAL_REKOMENDASI = datetime.utcnow()
        db.session.commit()
        update_user_profile(user_id, id_destinasi, alpha=0.05)
        try:
            cache.delete(f"reco:user:{user_id}:topn")
        except Exception:
            pass
        return jsonify({'status': 'wishlisted', 'success': True})
