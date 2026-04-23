# Sistem Rekomendasi Wisata — Development Readme

Langkah cepat untuk menjalankan aplikasi secara lokal (development, SQLite):

1. Buat environment virtual dan install depedencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. (Opsional) Download model FastText Indonesian pre-trained `cc.id.300.bin` dan simpan di `models/cc.id.300.bin`.
   Sumber: https://fasttext.cc/docs/en/crawl-vectors.html

3. Inisialisasi database development dan seed data:

```bash
python scripts/init_dev_db.py
```

4. (Jika model tersedia) jalankan preprocessing vektor destinasi:

```bash
python scripts/preprocess_vectors.py
```

5. Jalankan aplikasi:

```bash
python run.py
```

7. Menjalankan test suite

```bash
# Linux / macOS
./scripts/run_tests.sh

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest
pytest -q
```

6. Untuk menjalankan di production dengan Gunicorn:

```bash
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

Catatan:

- Untuk produksi gunakan Sybase SQL Anywhere seperti dijelaskan di `prd.md`.
- Jika FastText tidak tersedia, script preprocessing akan melewatkan pembuatan vektor.
