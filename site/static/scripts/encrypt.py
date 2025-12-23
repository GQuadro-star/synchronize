# static/scripts/encrypt.py
import base64
import hashlib
from cryptography.fernet import Fernet

def derive_key(raw_key: str) -> bytes:
    # Хешируем ключ SHA-256 → 32 байта
    digest = hashlib.sha256(raw_key.encode()).digest()
    # Кодируем в URL-safe base64 (для Fernet)
    return base64.urlsafe_b64encode(digest)

def process_file(b64data: str, original_filename: str, original_mime: str, key: str):
    key = derive_key(key)
    fernet = Fernet(key)

    result_b64 = base64.b64encode(fernet.encrypt(b64data.encode())).decode('ascii')
    result_filename = original_filename + '.processed'
    result_mime = original_mime or 'application/octet-stream'

    return {
        "result_b64": result_b64,
        "result_filename": result_filename,
        "result_mime": result_mime
    }