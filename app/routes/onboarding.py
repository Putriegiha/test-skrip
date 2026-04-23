from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.preferensi import PreferensiAwal
from app.models.pengguna import Pengguna
from app.services.vector_engine import init_user_profile

bp = Blueprint('onboarding', __name__, url_prefix='/onboarding')


@bp.route('/', methods=['GET', 'POST'])
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    pengguna = Pengguna.query.get(user_id)
    if pengguna and pengguna.IS_ONBOARDED:
        return redirect(url_for('rekomendasi.home'))

    categories = ['Alam', 'Buatan', 'Budaya', 'Desa']
    if request.method == 'POST':
        pilihan = request.form.getlist('kategori')
        if len(pilihan) != 2:
            flash('Pilih tepat 2 kategori.')
            return redirect(url_for('onboarding.index'))
        # simpan preferensi
        for k in pilihan:
            p = PreferensiAwal(ID_PENGGUNA=user_id, JENIS_WISATA=k)
            db.session.add(p)
        db.session.commit()
        # inisialisasi vektor profil
        init_user_profile(user_id, pilihan)
        session['is_onboarded'] = True
        return redirect(url_for('rekomendasi.home'))

    return render_template('onboarding.html', categories=categories)
