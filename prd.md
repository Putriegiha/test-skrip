# Product Requirements Document (PRD)

**Nama Produk:** Sistem Rekomendasi Wisata Adaptif Berbasis Semantic Content-Based Filtering  
**Platform:** Web Application (Responsive)  
**Framework:** Flask (Python)  
**Versi Dokumen:** 1.0  
**Tanggal:** April 2026  
**Status:** Draft — Ready for Engineering Review

---

## 1. Ringkasan Eksekutif

Sistem ini adalah platform cerdas pencarian dan rekomendasi destinasi wisata dengan fokus pada data **Jawa Timur**. Produk memecahkan masalah *information overload* saat pengguna mencari destinasi wisata dengan pendekatan **Semantic Content-Based Filtering** berbasis **FastText** dan **Cosine Similarity**.

Profil minat pengguna bersifat **dinamis** — terus beradaptasi setiap kali pengguna memberikan sinyal preferensi. Seluruh sistem dibangun di atas **Flask** (Python) dengan database **SAP Sybase SQL Anywhere** sesuai skema yang telah ditetapkan.

---

## 2. Struktur Database (Berdasarkan `db_egi.sql`)

Skema database yang digunakan mengacu pada file `db_egi.sql`. Berikut adalah mapping tabel dan peran fungsionalnya dalam sistem.

### 2.1 Tabel `DESTINASI_WISATA`

Menyimpan seluruh data destinasi wisata beserta vektor semantik hasil preprocessing.

```sql
create table DESTINASI_WISATA (
   ID_DESTINASI         integer         not null,
   KABUPATEN_KOTA       varchar(100)    not null,
   JENIS_WISATA         varchar(100)    not null,
   NAMA_DESTINASI       varchar(100)    not null,
   DESKRIPSI            long varchar    null,
   ALAMAT               long varchar    null,
   RATING               float           null,
   TOTAL_RATING         integer         null,
   TITIK_KOORDINAT      float           null,
   STATUS               smallint        null,
   constraint PK_DESTINASI_WISATA primary key (ID_DESTINASI)
);
```

**Catatan Pengembangan:**
- Kolom `STATUS` digunakan sebagai flag aktif/nonaktif (`1` = aktif, `0` = nonaktif). Hanya destinasi dengan `STATUS = 1` yang ditampilkan ke pengguna.
- Kolom `TITIK_KOORDINAT` saat ini bertipe `float` (satu nilai). Perlu diskusi apakah ini latitude atau akan dikembangkan menjadi dua kolom (`LAT`, `LNG`) di iterasi berikutnya.
- **Kolom Tambahan yang Diperlukan (ALTER):** Kolom `VEKTOR_ITEM` perlu ditambahkan untuk menyimpan hasil embedding FastText. Karena Sybase SQL Anywhere tidak memiliki ekstensi pgvector, vektor disimpan sebagai `LONG VARCHAR` (JSON array string) dan deserialisasi di sisi Python.

```sql
-- Tambahkan kolom vektor setelah tabel dibuat
ALTER TABLE DESTINASI_WISATA ADD VEKTOR_ITEM LONG VARCHAR NULL;
```

---

### 2.2 Tabel `PENGGUNA`

Menyimpan data akun pengguna.

```sql
create table PENGGUNA (
   ID_PENGGUNA     integer         not null,
   USERNAME        varchar(50)     not null,
   EMAIL           varchar(50)     not null,
   PASSWORD        varchar(50)     not null,
   TANGGAL_DAFTAR  date            not null,
   constraint PK_PENGGUNA primary key (ID_PENGGUNA)
);
```

**Catatan Pengembangan:**
- Kolom `PASSWORD` bertipe `varchar(50)`. Karena bcrypt hash menghasilkan string 60 karakter, kolom ini **harus di-ALTER** ke `varchar(255)` sebelum implementasi autentikasi.
- **Kolom Tambahan yang Diperlukan (ALTER):** `VEKTOR_PROFIL` (LONG VARCHAR), `IS_ONBOARDED` (smallint, default 0).

```sql
ALTER TABLE PENGGUNA ALTER PASSWORD varchar(255) NOT NULL;
ALTER TABLE PENGGUNA ADD VEKTOR_PROFIL LONG VARCHAR NULL;
ALTER TABLE PENGGUNA ADD IS_ONBOARDED smallint DEFAULT 0;
```

---

### 2.3 Tabel `PREFERENSI_AWAL`

Menyimpan 2 kategori jenis wisata yang dipilih pengguna saat Onboarding.

```sql
create table PREFERENSI_AWAL (
   ID_PREFERENSI   integer         not null,
   ID_PENGGUNA     integer         not null,
   JENIS_WISATA    varchar(100)    not null,
   constraint PK_PREFERENSI_AWAL primary key (ID_PREFERENSI)
);
```

**Catatan Pengembangan:**
- Setiap pengguna akan memiliki **tepat 2 baris** di tabel ini (satu per kategori yang dipilih).
- Foreign key ke `PENGGUNA(ID_PENGGUNA)` sudah terdefinisi di skema.
- Index `MEMILIKI2_FK` di skema asli kosong — perlu diperbaiki:

```sql
-- Perbaikan index FK yang kosong di skema asli
CREATE INDEX MEMILIKI2_FK ON PREFERENSI_AWAL (ID_PENGGUNA ASC);
```

---

### 2.4 Tabel `HISTORY_REKOMENDASI`

Menyimpan log rekomendasi yang diberikan sistem kepada pengguna, termasuk skor dari masing-masing algoritma.

```sql
create table HISTORY_REKOMENDASI (
   ID_HISTORY              integer     not null,
   ID_DESTINASI            integer     not null,
   ID_PENGGUNA             integer     not null,
   SKOR_CBF                float       not null,
   SKOR_KNN                float       not null,
   SKOR_HYBRID             float       not null,
   TANGGAL_REKOMENDASI     timestamp   not null,
   constraint PK_HISTORY_REKOMENDASI primary key (ID_HISTORY)
);
```

**Catatan Pengembangan:**
- Tabel ini mencatat **setiap rekomendasi** yang dimunculkan ke pengguna beserta skor algoritmanya (CBF = Content-Based Filtering, KNN = K-Nearest Neighbor, Hybrid = gabungan).
- Berguna untuk analitik dan evaluasi performa rekomendasi.
- **Kolom Tambahan yang Diperlukan (ALTER):** `TIPE_INTERAKSI` (`varchar(20)`, nilai: `'like'`, `'wishlist'`, `'view'`) dan `IS_INTERACTED` (`smallint`, default 0) untuk melacak apakah pengguna benar-benar berinteraksi dengan rekomendasi yang diberikan.

```sql
ALTER TABLE HISTORY_REKOMENDASI ADD TIPE_INTERAKSI varchar(20) NULL;
ALTER TABLE HISTORY_REKOMENDASI ADD IS_INTERACTED smallint DEFAULT 0;
```

---

### 2.5 Diagram Relasi Antar Tabel

```
PENGGUNA (ID_PENGGUNA)
    │
    ├──< PREFERENSI_AWAL (ID_PENGGUNA) — 1 pengguna, 2 baris preferensi
    │
    └──< HISTORY_REKOMENDASI (ID_PENGGUNA)
              │
              └──> DESTINASI_WISATA (ID_DESTINASI)
```

---

## 3. Arsitektur Aplikasi Flask

### 3.1 Struktur Direktori Proyek

```
wisata_app/
│
├── app/
│   ├── __init__.py              # Flask app factory, register blueprints
│   ├── config.py                # Konfigurasi DB, secret key, dll
│   │
│   ├── models/
│   │   ├── destinasi.py         # Model DESTINASI_WISATA
│   │   ├── pengguna.py          # Model PENGGUNA
│   │   ├── preferensi.py        # Model PREFERENSI_AWAL
│   │   └── history.py           # Model HISTORY_REKOMENDASI
│   │
│   ├── routes/
│   │   ├── auth.py              # Blueprint: /auth (login, register, logout)
│   │   ├── onboarding.py        # Blueprint: /onboarding
│   │   ├── rekomendasi.py       # Blueprint: / (beranda, detail)
│   │   ├── search.py            # Blueprint: /search
│   │   └── wishlist.py          # Blueprint: /wishlist
│   │
│   ├── services/
│   │   ├── vector_engine.py     # Cosine Similarity, Dynamic Profiling
│   │   ├── fasttext_service.py  # Load model FastText, generate embedding
│   │   └── cache_service.py     # Redis cache wrapper
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── onboarding.html
│   │   ├── home.html
│   │   ├── search.html
│   │   ├── detail.html
│   │   └── wishlist.html
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
│
├── scripts/
│   └── preprocess_vectors.py    # Script offline: generate & simpan VEKTOR_ITEM
│
├── requirements.txt
├── run.py                        # Entry point Flask
└── .env                          # Environment variables (tidak di-commit)
```

---

### 3.2 Konfigurasi Database (Sybase SQL Anywhere)

Flask menggunakan **SQLAlchemy** dengan driver `sqlalchemy-sqlany` atau koneksi via `pyodbc`.

```python
# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Sybase SQL Anywhere connection string
    SQLALCHEMY_DATABASE_URI = (
        f"sybase+pyodbc://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}"
        f"@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
        "?driver=SQL+Anywhere+17"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis untuk caching
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # FastText model path
    FASTTEXT_MODEL_PATH = os.environ.get('FASTTEXT_MODEL_PATH', 'models/cc.id.300.bin')
    
    # Bobot adaptasi profil
    LIKE_WEIGHT    = 0.10
    WISHLIST_WEIGHT = 0.05
    
    # Jumlah top rekomendasi
    TOP_N = 10
```

---

## 4. Kebutuhan Fungsional

### Fitur 1: Autentikasi Pengguna

**Deskripsi:** Modul registrasi, login, dan logout berbasis Flask session.

**Routes (Blueprint: `auth`):**

| Method | Route | Fungsi |
|---|---|---|
| GET, POST | `/auth/register` | Halaman & proses registrasi |
| GET, POST | `/auth/login` | Halaman & proses login |
| GET | `/auth/logout` | Proses logout, hapus session |

**Logika Backend (`routes/auth.py`):**

```python
# Register
# 1. Validasi: email unik di tabel PENGGUNA
# 2. Hash password dengan bcrypt
# 3. INSERT ke PENGGUNA (ID auto-increment, TANGGAL_DAFTAR = date.today())
# 4. Set session['user_id'] dan session['is_onboarded'] = False
# 5. Redirect ke /onboarding

# Login
# 1. Query PENGGUNA WHERE EMAIL = input
# 2. Verifikasi password dengan bcrypt.check_password_hash()
# 3. Set session['user_id'] dan session['is_onboarded']
# 4. Redirect ke / jika sudah onboarding, atau /onboarding jika belum
```

**Acceptance Criteria:**
- Registrasi berhasil dengan Username, Email unik, Password min. 8 karakter.
- Password di-hash bcrypt sebelum disimpan. Kolom `PASSWORD` di-ALTER ke `varchar(255)`.
- Login menghasilkan Flask session yang aman (`SESSION_COOKIE_HTTPONLY = True`).
- Logout menghapus seluruh session dan redirect ke `/auth/login`.
- Semua route yang membutuhkan login dilindungi decorator `@login_required`.

**Error States:**
- Email sudah terdaftar → flash message "Email sudah digunakan."
- Password salah / email tidak ditemukan → flash message generik "Email atau password salah."
- Akses route terproteksi tanpa login → redirect ke `/auth/login`.

---

### Fitur 2: Onboarding (Inisialisasi Preferensi)

**Deskripsi:** Halaman pemilihan 2 kategori wisata untuk membangun vektor profil awal pengguna.

**Routes (Blueprint: `onboarding`):**

| Method | Route | Fungsi |
|---|---|---|
| GET | `/onboarding` | Tampilkan halaman pilih kategori |
| POST | `/onboarding` | Proses pilihan, hitung vektor, redirect |

**Logika Backend (`routes/onboarding.py`):**

```python
# GET /onboarding
# 1. Cek session: jika IS_ONBOARDED = 1, redirect ke /
# 2. Render template dengan 4 pilihan kategori

# POST /onboarding
# 1. Ambil form data: list kategori yang dipilih
# 2. Validasi: harus tepat 2 item
# 3. INSERT 2 baris ke PREFERENSI_AWAL (ID_PENGGUNA, JENIS_WISATA)
# 4. Panggil vector_engine.init_user_profile(id_pengguna, [kat1, kat2])
#    → Ambil semua VEKTOR_ITEM dari DESTINASI_WISATA WHERE JENIS_WISATA IN (kat1, kat2)
#    → Hitung rata-rata vektor → L2 normalize
#    → UPDATE PENGGUNA SET VEKTOR_PROFIL = json.dumps(vektor), IS_ONBOARDED = 1
# 5. Update session['is_onboarded'] = True
# 6. Redirect ke /
```

**Acceptance Criteria:**
- Menampilkan 4 chip/tombol: **Wisata Alam, Wisata Buatan, Wisata Budaya, Desa Wisata**.
- Tombol "Lanjutkan" hanya aktif jika tepat 2 kategori terpilih (validasi JavaScript + validasi server-side).
- Setelah submit, 2 baris tersimpan di `PREFERENSI_AWAL`.
- Vektor profil awal tersimpan di kolom `VEKTOR_PROFIL` tabel `PENGGUNA`.
- Pengguna yang sudah onboarding tidak bisa akses halaman ini kembali.

---

### Fitur 3: Beranda Personalisasi

**Deskripsi:** Halaman utama yang menampilkan Top-N rekomendasi berdasarkan Cosine Similarity.

**Routes (Blueprint: `rekomendasi`):**

| Method | Route | Fungsi |
|---|---|---|
| GET | `/` | Beranda dengan Top-N rekomendasi |
| GET | `/destinasi/<id_destinasi>` | Halaman detail destinasi |
| POST | `/destinasi/<id_destinasi>/like` | Toggle like, update profil |
| POST | `/destinasi/<id_destinasi>/wishlist` | Toggle wishlist, update profil |

**Logika Backend (`routes/rekomendasi.py`):**

```python
# GET /
# 1. Ambil VEKTOR_PROFIL pengguna dari DB (atau cache Redis)
# 2. Ambil semua DESTINASI_WISATA WHERE STATUS = 1
# 3. Untuk setiap destinasi, hitung cosine_similarity(vektor_profil, vektor_item)
# 4. Sort descending berdasarkan skor similarity
# 5. Ambil Top-N
# 6. Log ke HISTORY_REKOMENDASI (ID_PENGGUNA, ID_DESTINASI, SKOR_CBF, SKOR_KNN=0, 
#    SKOR_HYBRID=skor_cbf, TANGGAL_REKOMENDASI=now())
# 7. Render home.html dengan list destinasi + skor (skor tidak ditampilkan ke user)
```

**Acceptance Criteria:**
- Menampilkan Top-10 destinasi dengan urutan 100% berdasarkan Cosine Similarity.
- Card menampilkan: Nama, Kabupaten/Kota, Jenis Wisata, Rating, tombol Like/Wishlist.
- Setiap sesi beranda baru dicatat di `HISTORY_REKOMENDASI`.
- Hasil rekomendasi di-cache di Redis (TTL 5 menit), diinvalidasi saat ada interaksi baru.

---

### Fitur 4: Pencarian & Filter

**Deskripsi:** Filter berbasis SQL diikuti ranking semantik personal.

**Routes (Blueprint: `search`):**

| Method | Route | Fungsi |
|---|---|---|
| GET | `/search` | Halaman search dengan dropdown filter |

**Logika Backend (`routes/search.py`):**

```python
# GET /search?kabupaten=Malang&jenis=Alam
# 1. Bangun query SQL dengan hard filter:
#    SELECT * FROM DESTINASI_WISATA WHERE STATUS = 1
#    [AND KABUPATEN_KOTA = :kabupaten] (jika ada)
#    [AND JENIS_WISATA = :jenis] (jika ada)
# 2. Dari hasil query, hitung cosine_similarity terhadap VEKTOR_PROFIL pengguna
# 3. Sort descending
# 4. Render search.html dengan hasil
```

**Acceptance Criteria:**
- Tersedia 2 dropdown: Kabupaten/Kota (dari `DISTINCT KABUPATEN_KOTA` di DB) dan Jenis Wisata.
- Kedua filter opsional; jika kosong, semua data diikutkan.
- Jika hasil kosong → tampilkan pesan dengan tombol "Reset Filter".
- Data dropdown diambil dinamis dari database.

---

### Fitur 5: Like & Wishlist (Interaksi)

**Deskripsi:** Aksi pengguna yang memperbarui profil vektor secara dinamis.

**Logika Backend (dalam `routes/rekomendasi.py`):**

```python
# POST /destinasi/<id_destinasi>/like
# 1. Cek di HISTORY_REKOMENDASI: apakah sudah ada record LIKE untuk user + destinasi ini?
#    → Jika sudah ada (IS_INTERACTED=1, TIPE_INTERAKSI='like'): 
#       UPDATE SET IS_INTERACTED=0 (unlike) — profil TIDAK diubah
#    → Jika belum:
#       UPDATE HISTORY_REKOMENDASI SET IS_INTERACTED=1, TIPE_INTERAKSI='like'
#       Panggil vector_engine.update_profile(id_pengguna, vektor_item, alpha=0.10)
#       Invalidasi cache Redis
# 2. Return JSON { "status": "liked" | "unliked", "success": true }

# POST /destinasi/<id_destinasi>/wishlist  
# Sama dengan like, alpha=0.05, TIPE_INTERAKSI='wishlist'
```

**Acceptance Criteria:**
- Like dan Wishlist bersifat toggle.
- Setiap interaksi memperbarui kolom `TIPE_INTERAKSI` dan `IS_INTERACTED` di `HISTORY_REKOMENDASI`.
- Status Like/Wishlist tercermin di semua tampilan card secara konsisten.

---

### Fitur 6: Halaman Wishlist

**Routes (Blueprint: `wishlist`):**

| Method | Route | Fungsi |
|---|---|---|
| GET | `/wishlist` | Daftar destinasi yang di-wishlist |

**Logika Backend:**

```python
# GET /wishlist
# SELECT d.* FROM DESTINASI_WISATA d
# JOIN HISTORY_REKOMENDASI h ON d.ID_DESTINASI = h.ID_DESTINASI
# WHERE h.ID_PENGGUNA = :id_pengguna
#   AND h.TIPE_INTERAKSI = 'wishlist'
#   AND h.IS_INTERACTED = 1
# ORDER BY h.TANGGAL_REKOMENDASI DESC
```

---

## 5. Arsitektur Algoritma (Core Engine)

### 5.1 Script Preprocessing Offline (`scripts/preprocess_vectors.py`)

Dijalankan sekali saat setup awal, dan diulang jika ada data baru.

```python
import fasttext
import json
import numpy as np
from app import create_app, db
from app.models.destinasi import DestinasiWisata

def preprocess_and_store():
    app = create_app()
    with app.app_context():
        # 1. Load model FastText
        model = fasttext.load_model('models/cc.id.300.bin')
        
        # 2. Ambil semua destinasi
        destinasi_list = DestinasiWisata.query.filter_by(STATUS=1).all()
        
        for dest in destinasi_list:
            # 3. Preprocessing teks
            teks = clean_text(dest.DESKRIPSI or dest.NAMA_DESTINASI)
            
            # 4. Generate semantic vector (average word vectors)
            words = teks.split()
            word_vectors = [model.get_word_vector(w) for w in words if w]
            if not word_vectors:
                continue
            v_semantic = np.mean(word_vectors, axis=0)  # shape: (300,)
            
            # 5. One-hot encoding jenis wisata
            jenis_map = {'Alam': 0, 'Buatan': 1, 'Budaya': 2, 'Desa': 3}
            v_jenis = np.zeros(4)
            idx = jenis_map.get(dest.JENIS_WISATA)
            if idx is not None:
                v_jenis[idx] = 1.0
            
            # 6. Normalisasi rating
            rating_norm = (dest.RATING or 0) / 5.0
            v_rating = np.array([rating_norm])
            
            # 7. Gabungkan & L2 normalize
            v_final = np.concatenate([v_semantic, 1.0 * v_jenis, 0.2 * v_rating])
            norm = np.linalg.norm(v_final)
            if norm > 0:
                v_final = v_final / norm
            
            # 8. Simpan ke DB sebagai JSON string
            dest.VEKTOR_ITEM = json.dumps(v_final.tolist())
        
        db.session.commit()
        print(f"Selesai: {len(destinasi_list)} destinasi diproses.")

def clean_text(teks: str) -> str:
    import re
    teks = teks.lower()
    teks = re.sub(r'[^a-z\s]', '', teks)
    # TODO: tambahkan stopword removal (PySastrawi atau list manual)
    return teks.strip()
```

---

### 5.2 Vector Engine Service (`services/vector_engine.py`)

```python
import json
import numpy as np
from app.models.pengguna import Pengguna
from app.models.destinasi import DestinasiWisata
from app import db

def cosine_similarity(v1: list, v2: list) -> float:
    """Hitung cosine similarity antara dua vektor (sudah L2-normalized = dot product)."""
    a = np.array(v1)
    b = np.array(v2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def get_top_n_recommendations(id_pengguna: int, n: int = 10, 
                               filter_kota: str = None, 
                               filter_jenis: str = None) -> list:
    """Ambil Top-N rekomendasi untuk pengguna."""
    pengguna = Pengguna.query.get(id_pengguna)
    if not pengguna or not pengguna.VEKTOR_PROFIL:
        return []
    
    v_profil = json.loads(pengguna.VEKTOR_PROFIL)
    
    # Hard filter di level DB
    query = DestinasiWisata.query.filter_by(STATUS=1)
    if filter_kota:
        query = query.filter_by(KABUPATEN_KOTA=filter_kota)
    if filter_jenis:
        query = query.filter_by(JENIS_WISATA=filter_jenis)
    
    destinasi_list = query.all()
    
    # Hitung similarity
    scored = []
    for dest in destinasi_list:
        if not dest.VEKTOR_ITEM:
            continue
        v_item = json.loads(dest.VEKTOR_ITEM)
        skor = cosine_similarity(v_profil, v_item)
        scored.append((dest, skor))
    
    # Sort descending, ambil Top-N
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:n]

def update_user_profile(id_pengguna: int, id_destinasi: int, alpha: float):
    """
    Dynamic Profiling: geser vektor profil mendekati vektor item.
    Formula: V_u_baru = normalize(V_u + alpha * (V_i - V_u))
    """
    pengguna = Pengguna.query.get(id_pengguna)
    dest = DestinasiWisata.query.get(id_destinasi)
    
    if not pengguna or not pengguna.VEKTOR_PROFIL or not dest or not dest.VEKTOR_ITEM:
        return
    
    v_u = np.array(json.loads(pengguna.VEKTOR_PROFIL))
    v_i = np.array(json.loads(dest.VEKTOR_ITEM))
    
    v_u_baru = v_u + alpha * (v_i - v_u)
    
    # L2 normalize
    norm = np.linalg.norm(v_u_baru)
    if norm > 0:
        v_u_baru = v_u_baru / norm
    
    pengguna.VEKTOR_PROFIL = json.dumps(v_u_baru.tolist())
    db.session.commit()

def init_user_profile(id_pengguna: int, kategori_list: list):
    """
    Inisialisasi vektor profil dari Onboarding.
    Rata-rata semua VEKTOR_ITEM dengan JENIS_WISATA dalam kategori_list.
    """
    destinasi_list = DestinasiWisata.query.filter(
        DestinasiWisata.JENIS_WISATA.in_(kategori_list),
        DestinasiWisata.STATUS == 1,
        DestinasiWisata.VEKTOR_ITEM.isnot(None)
    ).all()
    
    if not destinasi_list:
        return
    
    vektors = [np.array(json.loads(d.VEKTOR_ITEM)) for d in destinasi_list]
    v_rata = np.mean(vektors, axis=0)
    
    # L2 normalize
    norm = np.linalg.norm(v_rata)
    if norm > 0:
        v_rata = v_rata / norm
    
    pengguna = Pengguna.query.get(id_pengguna)
    pengguna.VEKTOR_PROFIL = json.dumps(v_rata.tolist())
    pengguna.IS_ONBOARDED = 1
    db.session.commit()
```

---

### 5.3 Bobot Adaptasi Profil

| Aksi | Alpha (α) | Efek |
|---|---|---|
| **Like** | 0.10 | Profil bergeser 10% mendekati item |
| **Wishlist** | 0.05 | Profil bergeser 5% mendekati item |
| **Unlike / Hapus Wishlist** | — | Profil **tidak berubah** (by design) |

---

## 6. Perubahan Skema Database yang Diperlukan

Berikut adalah seluruh perubahan `ALTER TABLE` yang harus dijalankan terhadap `db_egi.sql` sebelum aplikasi dijalankan:

```sql
-- 1. Perbaiki panjang kolom PASSWORD agar dapat menampung bcrypt hash (60 char)
ALTER TABLE PENGGUNA ALTER PASSWORD varchar(255) NOT NULL;

-- 2. Tambah kolom vektor profil pengguna
ALTER TABLE PENGGUNA ADD VEKTOR_PROFIL LONG VARCHAR NULL;

-- 3. Tambah flag status onboarding
ALTER TABLE PENGGUNA ADD IS_ONBOARDED smallint DEFAULT 0 NOT NULL;

-- 4. Tambah kolom vektor item destinasi
ALTER TABLE DESTINASI_WISATA ADD VEKTOR_ITEM LONG VARCHAR NULL;

-- 5. Tambah kolom tipe interaksi pada history
ALTER TABLE HISTORY_REKOMENDASI ADD TIPE_INTERAKSI varchar(20) NULL;

-- 6. Tambah flag apakah rekomendasi ini diinteraksikan
ALTER TABLE HISTORY_REKOMENDASI ADD IS_INTERACTED smallint DEFAULT 0 NOT NULL;

-- 7. Perbaiki index MEMILIKI2_FK yang kosong di skema asli
CREATE INDEX MEMILIKI2_FK ON PREFERENSI_AWAL (ID_PENGGUNA ASC);
```

---

## 7. Kebutuhan Non-Fungsional

### 7.1 Performa
- Waktu respons halaman beranda (p95): < 2 detik.
- Kalkulasi similarity untuk ≤ 1.000 item: < 500ms di Python.
- Cache Redis pada rekomendasi beranda (TTL 5 menit), diinvalidasi setiap ada Like/Wishlist.

### 7.2 Keamanan
- Semua route terproteksi menggunakan decorator `@login_required` kustom yang mengecek `session['user_id']`.
- Password di-hash dengan `bcrypt` (via `flask-bcrypt`).
- Input dari form di-escape via Jinja2 auto-escaping. Form menggunakan CSRF token (`Flask-WTF`).
- Konfigurasi session: `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`.
- Rate limiting pada endpoint login (via `Flask-Limiter`): maks 5 percobaan per 15 menit per IP.

### 7.3 Skalabilitas
- Model FastText (`cc.id.300.bin`) dimuat ke memori **sekali saat startup** menggunakan application context Flask, tidak di-reload per request.
- Minimum RAM server yang direkomendasikan: **8GB** (model FastText ~4.2GB).
- Gunakan Gunicorn sebagai WSGI server dengan beberapa worker process.

---

## 8. Dependencies (`requirements.txt`)

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Bcrypt==1.0.1
Flask-WTF==1.2.1
Flask-Limiter==3.7.0
pyodbc==5.1.0              # Koneksi Sybase SQL Anywhere
fasttext-wheel==0.9.2      # FastText Python binding
numpy==1.26.4
redis==5.0.4
python-dotenv==1.0.1
gunicorn==22.0.0
```

---

## 9. Skenario Uji

### 9.1 Uji Fungsional

| ID | Skenario | Expected Result |
|---|---|---|
| F-01 | Register dengan email yang sudah ada | Flash: "Email sudah digunakan", redirect ke register |
| F-02 | Login dengan password salah | Flash: "Email atau password salah" |
| F-03 | Akses `/` tanpa login | Redirect ke `/auth/login` |
| F-04 | Submit onboarding dengan 1 kategori | Server tolak dengan validasi error |
| F-05 | Submit onboarding dengan 3 kategori | Server tolak dengan validasi error |
| F-06 | Klik Like pada destinasi | `IS_INTERACTED=1` di DB, profil diperbarui, cache invalidasi |
| F-07 | Klik Like lagi (unlike) | `IS_INTERACTED=0` di DB, profil tidak berubah |
| F-08 | Search filter Kota=Malang, Jenis=Alam | Hanya destinasi Alam di Malang tampil |
| F-09 | Search tanpa filter | Semua destinasi aktif tampil, diurutkan similarity |

### 9.2 Uji Algoritma

| ID | Skenario | Expected Result |
|---|---|---|
| A-01 | User like 5 destinasi pantai Malang, lalu search di Bangkalan | Wisata pantai/bahari Bangkalan di peringkat atas |
| A-02 | User A onboarding "Alam"+"Budaya" vs User B "Buatan"+"Desa" | Urutan beranda keduanya berbeda |
| A-03 | Vektor profil setelah Like vs sebelum | `VEKTOR_PROFIL` di DB berubah; dot product dengan destinasi yang di-like meningkat |

### 9.3 Uji Database

| ID | Skenario | Expected Result |
|---|---|---|
| D-01 | Onboarding selesai | 2 baris di `PREFERENSI_AWAL`, `IS_ONBOARDED=1` di `PENGGUNA` |
| D-02 | Beranda dimuat | Baris baru di `HISTORY_REKOMENDASI` untuk setiap Top-N item |
| D-03 | Script `preprocess_vectors.py` dijalankan | Semua baris `DESTINASI_WISATA` punya `VEKTOR_ITEM` tidak null |

---

## 10. Rencana Rilis (Milestone)

### Milestone 1 — Setup & Foundation
- [ ] Inisialisasi proyek Flask dengan struktur direktori
- [ ] Konfigurasi koneksi Sybase SQL Anywhere via SQLAlchemy
- [ ] Jalankan `db_egi.sql` + semua `ALTER TABLE` yang diperlukan
- [ ] Implementasi autentikasi (register, login, logout)

### Milestone 2 — Core Algorithm
- [ ] Download dan test model FastText `cc.id.300.bin`
- [ ] Implementasi `scripts/preprocess_vectors.py`
- [ ] Implementasi `services/vector_engine.py`
- [ ] Unit test cosine similarity dan dynamic profiling

### Milestone 3 — Fitur Utama
- [ ] Onboarding (pilih 2 kategori, init profil)
- [ ] Beranda personalisasi + logging ke `HISTORY_REKOMENDASI`
- [ ] Search & Filter
- [ ] Like & Wishlist + update profil

### Milestone 4 — Polish & Launch
- [ ] Template HTML + TailwindCSS (Jinja2)
- [ ] Implementasi Redis caching
- [ ] Testing lengkap (fungsional, algoritma, DB)
- [ ] Deploy dengan Gunicorn

---

## 11. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| RAM tidak cukup untuk model FastText | Tinggi | Gunakan model distilasi atau lazy loading; evaluasi API embedding eksternal |
| Driver Sybase (`pyodbc`) sulit dikonfigurasi | Sedang | Siapkan fallback ke SQLite untuk development lokal |
| Deskripsi destinasi pendek / kosong | Tinggi | Fallback ke `NAMA_DESTINASI` jika `DESKRIPSI` < 20 karakter |
| Vektor JSON tersimpan terlalu besar (300 float) | Rendah | ~1.2KB per baris — tidak signifikan untuk ribuan baris |
| `HISTORY_REKOMENDASI` tumbuh sangat besar | Sedang | Tambahkan job purge data lebih dari 90 hari di iterasi berikutnya |

---

## Lampiran A: Mapping Nilai `JENIS_WISATA`

Nilai pada kolom `JENIS_WISATA` di tabel `DESTINASI_WISATA` dan `PREFERENSI_AWAL` harus konsisten menggunakan nilai berikut:

| Nilai di DB | Label Tampilan |
|---|---|
| `Alam` | Wisata Alam |
| `Buatan` | Wisata Buatan |
| `Budaya` | Wisata Budaya |
| `Desa` | Desa Wisata |

---

## Lampiran B: Glosarium

| Istilah | Definisi |
|---|---|
| **CBF (Content-Based Filtering)** | Metode rekomendasi berdasarkan kemiripan konten item dengan profil pengguna. Skor ini disimpan di kolom `SKOR_CBF`. |
| **KNN** | K-Nearest Neighbor — metode alternatif atau pelengkap CBF. Kolom `SKOR_KNN` disediakan untuk ekspansi di masa depan. |
| **Cosine Similarity** | Ukuran kemiripan dua vektor berdasarkan sudut di antaranya. |
| **FastText** | Model embedding dari Meta AI yang mampu menangani kata di luar kosakata dengan subword. |
| **Centroid Displacement** | Teknik menggeser titik tengah profil pengguna mendekati item yang disukai. |
| **L2 Normalization** | Membagi vektor dengan panjangnya agar semua vektor bersatuan panjang 1. |
| **Flask Blueprint** | Komponen modular Flask untuk memisahkan logika route per fitur. |
| **SKOR_HYBRID** | Gabungan SKOR_CBF dan SKOR_KNN. Pada implementasi ini = SKOR_CBF karena KNN belum diimplementasikan. |

---

*Dokumen ini adalah living document. Setiap perubahan skema atau logika algoritma harus diperbarui di sini sebelum diimplementasikan.*
