import base64
import hashlib
import time
import random
import string
from cryptography.fernet import Fernet, InvalidToken

SYNC_SIGNATURE = b"SYNC_ENC_V1:"

def generate_unique_name(original_filename: str) -> str:
    """Генерирует уникальное имя в формате {random}.{ext}.enc"""
    # Получаем оригинальное расширение
    ext = original_filename.split('.')[-1] if '.' in original_filename else 'bin'
    # Генерируем уникальный префикс
    prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    timestamp = int(time.time())
    return f"{prefix}{timestamp}.{ext}.enc"

def derive_key(raw_key: str) -> bytes:
    digest = hashlib.sha256(raw_key.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def process_file(b64data: str, original_filename: str, original_mime: str, key: str, mode: str = "encrypt"):
    fernet = Fernet(derive_key(key))
    result_mime = original_mime or 'application/octet-stream'

    if mode == "encrypt":
        # Шифруем данные
        encrypted_data = fernet.encrypt(b64data.encode())
        payload = SYNC_SIGNATURE + base64.b64encode(encrypted_data)
        result_b64 = base64.b64encode(payload).decode('ascii')
        
        # Генерируем уникальное имя (без оригинального названия)
        result_filename = generate_unique_name(original_filename)

    elif mode == "decrypt":
        decoded_payload = base64.b64decode(b64data)
        
        if not decoded_payload.startswith(SYNC_SIGNATURE):
            raise ValueError("Файл не является зашифрованным .enc")
        
        encrypted_b64 = decoded_payload[len(SYNC_SIGNATURE):]
        encrypted_data = base64.b64decode(encrypted_b64)
        
        try:
            decrypted_b64 = fernet.decrypt(encrypted_data).decode()
        except InvalidToken:
            raise ValueError("Неверный ключ расшифровки")
        
        result_b64 = decrypted_b64
        # Удаляем .enc и сохраняем структуру {unique}.{ext}
        if original_filename.endswith('.enc'):
            result_filename = original_filename[:-4]
        else:
            result_filename = "decrypted_" + original_filename

    else:
        raise ValueError("Неизвестный режим обработки")

    return {
        "result_b64": result_b64,
        "result_filename": result_filename,
        "result_mime": result_mime,
        "mode": mode
    }