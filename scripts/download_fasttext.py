"""Download pretrained FastText cc.id.300.bin if not present.
This script downloads the file from fastText crawl vectors mirror (user must verify license).
"""
import os
import sys
import urllib.request

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'cc.id.300.bin')
DOWNLOAD_URL = 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.id.300.bin.gz'

def ensure_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if os.path.exists(MODEL_PATH):
        print('Model already exists:', MODEL_PATH)
        return
    gz_path = MODEL_PATH + '.gz'
    print('Downloading', DOWNLOAD_URL)
    try:
        urllib.request.urlretrieve(DOWNLOAD_URL, gz_path)
    except Exception as e:
        print('Download failed:', e)
        sys.exit(1)
    # decompress
    import gzip
    try:
        with gzip.open(gz_path, 'rb') as f_in, open(MODEL_PATH, 'wb') as f_out:
            f_out.write(f_in.read())
        os.remove(gz_path)
        print('Model downloaded and extracted to', MODEL_PATH)
    except Exception as e:
        print('Extraction failed:', e)
        sys.exit(1)

if __name__ == '__main__':
    ensure_model()
