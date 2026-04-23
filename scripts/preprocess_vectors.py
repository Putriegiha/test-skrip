import json
import numpy as np
from app import create_app, db
from app.models.destinasi import DestinasiWisata

def clean_text(teks: str) -> str:
    import re
    teks = (teks or '').lower()
    teks = re.sub(r'[^a-z\s]', '', teks)
    return teks.strip()

def preprocess_and_store(model):
    app = create_app()
    with app.app_context():
        destinasi_list = DestinasiWisata.query.filter_by(STATUS=1).all()
        for dest in destinasi_list:
            teks = clean_text(dest.DESKRIPSI or dest.NAMA_DESTINASI)
            words = teks.split()
            word_vectors = [model.get_word_vector(w) for w in words if w]
            if not word_vectors:
                continue
            v_semantic = np.mean(word_vectors, axis=0)
            jenis_map = {'Alam': 0, 'Buatan': 1, 'Budaya': 2, 'Desa': 3}
            v_jenis = np.zeros(4)
            idx = jenis_map.get(dest.JENIS_WISATA)
            if idx is not None:
                v_jenis[idx] = 1.0
            rating_norm = (dest.RATING or 0) / 5.0
            v_rating = np.array([rating_norm])
            v_final = np.concatenate([v_semantic, 1.0 * v_jenis, 0.2 * v_rating])
            norm = np.linalg.norm(v_final)
            if norm > 0:
                v_final = v_final / norm
            dest.VEKTOR_ITEM = json.dumps(v_final.tolist())
        db.session.commit()
        print(f"Selesai: {len(destinasi_list)} destinasi diproses.")

if __name__ == '__main__':
    try:
        import fasttext
        model = fasttext.load_model('models/cc.id.300.bin')
    except Exception as e:
        print('FastText model not available:', e)
        model = None
    if model:
        preprocess_and_store(model)
