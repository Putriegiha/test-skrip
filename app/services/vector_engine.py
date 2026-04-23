import json
import numpy as np
from app.models.pengguna import Pengguna
from app.models.destinasi import DestinasiWisata
from app import db

def cosine_similarity(v1, v2):
    a = np.array(v1)
    b = np.array(v2)
    if a.size == 0 or b.size == 0:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def get_top_n_recommendations(id_pengguna, n=10, filter_kota=None, filter_jenis=None):
    pengguna = Pengguna.query.get(id_pengguna)
    if not pengguna or not pengguna.VEKTOR_PROFIL:
        return []
    v_profil = json.loads(pengguna.VEKTOR_PROFIL)
    query = DestinasiWisata.query.filter_by(STATUS=1)
    if filter_kota:
        query = query.filter_by(KABUPATEN_KOTA=filter_kota)
    if filter_jenis:
        query = query.filter_by(JENIS_WISATA=filter_jenis)
    destinasi_list = query.all()
    scored = []
    for dest in destinasi_list:
        if not dest.VEKTOR_ITEM:
            continue
        v_item = json.loads(dest.VEKTOR_ITEM)
        skor = cosine_similarity(v_profil, v_item)
        scored.append((dest, skor))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:n]

def update_user_profile(id_pengguna, id_destinasi, alpha):
    pengguna = Pengguna.query.get(id_pengguna)
    dest = DestinasiWisata.query.get(id_destinasi)
    if not pengguna or not pengguna.VEKTOR_PROFIL or not dest or not dest.VEKTOR_ITEM:
        return
    v_u = np.array(json.loads(pengguna.VEKTOR_PROFIL))
    v_i = np.array(json.loads(dest.VEKTOR_ITEM))
    v_u_baru = v_u + alpha * (v_i - v_u)
    norm = np.linalg.norm(v_u_baru)
    if norm > 0:
        v_u_baru = v_u_baru / norm
    pengguna.VEKTOR_PROFIL = json.dumps(v_u_baru.tolist())
    db.session.commit()

def init_user_profile(id_pengguna, kategori_list):
    destinasi_list = DestinasiWisata.query.filter(
        DestinasiWisata.JENIS_WISATA.in_(kategori_list),
        DestinasiWisata.STATUS == 1,
        DestinasiWisata.VEKTOR_ITEM.isnot(None)
    ).all()
    if not destinasi_list:
        return
    vektors = [np.array(json.loads(d.VEKTOR_ITEM)) for d in destinasi_list]
    v_rata = np.mean(vektors, axis=0)
    norm = np.linalg.norm(v_rata)
    if norm > 0:
        v_rata = v_rata / norm
    pengguna = Pengguna.query.get(id_pengguna)
    pengguna.VEKTOR_PROFIL = json.dumps(v_rata.tolist())
    pengguna.IS_ONBOARDED = 1
    db.session.commit()
