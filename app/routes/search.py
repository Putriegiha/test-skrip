from flask import Blueprint, render_template, request, session, redirect, url_for
from app.utils import login_required
from app.models.destinasi import DestinasiWisata
from app.services.vector_engine import get_top_n_recommendations

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('', methods=['GET'])
@login_required
def index():
    user_id = session.get('user_id')
    kabupaten = request.args.get('kabupaten')
    jenis = request.args.get('jenis')

    # For dropdown values
    kota_list = [r[0] for r in DestinasiWisata.query.with_entities(DestinasiWisata.KABUPATEN_KOTA).distinct().all()]
    jenis_list = [r[0] for r in DestinasiWisata.query.with_entities(DestinasiWisata.JENIS_WISATA).distinct().all()]

    scored = get_top_n_recommendations(user_id, n=100, filter_kota=kabupaten, filter_jenis=jenis)
    results = [d for d, s in scored]
    return render_template('search.html', results=results, kota_list=kota_list, jenis_list=jenis_list, selected_kab=kabupaten, selected_jenis=jenis)
