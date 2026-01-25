import base64
import time
import secrets
import os
from typing import Dict, Union
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SYNC_SIGNATURE = b"SYNCHRONIZE_V1_"
SALT_SIZE = 16
KDF_ITERATIONS = 600_000
KDF_ALGORITHM = hashes.SHA256()

def generate_unique_name(original_filename: str) -> str:
    ext = original_filename.split('.')[-1] if '.' in original_filename else 'bin'
    prefix = secrets.token_urlsafe(12)
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}.{ext}.enc"

def _derive_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=KDF_ALGORITHM,
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def _add_padding(data: str) -> str:
    return data + '=' * (-len(data) % 4)

def process_file(
    data: Union[str, bytes],
    original_filename: str,
    original_mime: str,
    password: str,
    mode: str = "encrypt"
) -> Dict[str, str]:
    if mode == "encrypt":
        result_mime = 'application/octet-stream'
    else:
        result_mime = original_mime or 'application/octet-stream'
    
    if mode == "encrypt":
        if isinstance(data, str):
            data = _add_padding(data)
            raw_data = base64.b64decode(data)
        else:
            raw_data = data
        
        salt = os.urandom(SALT_SIZE)
        key = _derive_key_from_password(password, salt)
        fernet = Fernet(key)
        
        encrypted_data = fernet.encrypt(raw_data)
        
        # Формируем payload в бинарном виде
        payload = SYNC_SIGNATURE + salt + encrypted_data
        
        # Кодируем ВЕСЬ payload в base64 для сохранения
        result_b64 = base64.b64encode(payload).decode('ascii')
        result_filename = generate_unique_name(original_filename)
        
    elif mode == "decrypt":
        data = _add_padding(data)
        
        try:
            decoded_payload = base64.b64decode(data)
        except Exception as e:
            raise ValueError(f"Ошибка декодирования base64: {str(e)}")
        
        # Проверяем сигнатуру
        if not decoded_payload.startswith(SYNC_SIGNATURE):
            preview = decoded_payload[:20]
            raise ValueError(f"Неверная сигнатура файла. Данные начинаются с: {preview.hex()}")
        
        # Извлекаем соль и зашифрованные данные
        salt_start = len(SYNC_SIGNATURE)
        salt = decoded_payload[salt_start:salt_start + SALT_SIZE]
        encrypted_data = decoded_payload[salt_start + SALT_SIZE:]
        
        # Создаем ключ и расшифровываем
        key = _derive_key_from_password(password, salt)
        fernet = Fernet(key)
        
        try:
            raw_data = fernet.decrypt(encrypted_data)
        except InvalidToken:
            raise ValueError("Неверный пароль или поврежденные данные")
        
        result_b64 = base64.b64encode(raw_data).decode('ascii')
        
        if original_filename.endswith('.enc'):
            result_filename = original_filename[:-4]
        else:
            result_filename = "decrypted_" + original_filename
    else:
        raise ValueError("Неизвестный режим обработки: должен быть 'encrypt' или 'decrypt'")

    return {
        "result_b64": result_b64,
        "result_filename": result_filename,
        "result_mime": result_mime,
        "mode": mode
    }