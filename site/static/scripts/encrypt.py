import base64
import time
import secrets
import os
from typing import Dict, Union
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SYNC_SIGNATURE = b"SYNCHRONIZE_V1:"

SALT_SIZE = 16
KDF_ITERATIONS = 600_000
KDF_ALGORITHM = hashes.SHA256()


def generate_unique_name(original_filename: str) -> str:
    ext = original_filename.split('.')[-1] if '.' in original_filename else 'bin'
    prefix = secrets.token_urlsafe(12)  # криптостойкий генератор
    timestamp = int(time.time())
    return f"{prefix}{timestamp}.{ext}.enc"


def _derive_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=KDF_ALGORITHM,
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def process_file(
    data: Union[str, bytes],
    original_filename: str,
    original_mime: str,
    password: str,
    mode: str = "encrypt"
) -> Dict[str, str]:

    result_mime = original_mime or 'application/octet-stream'

    if mode == "encrypt":
        if isinstance(data, str):
            raw_data = base64.b64decode(data)
        else:
            raw_data = data

        salt = os.urandom(SALT_SIZE)
        key = _derive_key_from_password(password, salt)
        fernet = Fernet(key)

        # Шифруем
        encrypted_data = fernet.encrypt(raw_data)

        # Собираем payload: SYNC_ENC_V2:<base64(salt)>:<base64(encrypted)>
        payload = (
            SYNC_SIGNATURE + b":" +
            base64.b64encode(salt) + b":" +
            base64.b64encode(encrypted_data)
        )

        result_b64 = base64.b64encode(payload).decode('ascii')
        result_filename = generate_unique_name(original_filename)

    elif mode == "decrypt":
        # Декодируем внешний base64
        try:
            decoded_payload = base64.b64decode(data)
        except Exception as e:
            raise ValueError("Неверный формат base64") from e

        # Проверяем сигнатуру
        if not decoded_payload.startswith(SYNC_SIGNATURE + b":"):
            raise ValueError("Файл не является зашифрованным .enc (неверная сигнатура)")

        parts = decoded_payload.split(b":", 2)
        if len(parts) != 3:
            raise ValueError("Повреждённая структура файла")

        _, salt_b64, encrypted_b64 = parts

        try:
            salt = base64.b64decode(salt_b64)
            encrypted_data = base64.b64decode(encrypted_b64)
        except Exception as e:
            raise ValueError("Неверное кодирование соли или данных") from e

        # Восстанавливаем ключ
        key = _derive_key_from_password(password, salt)
        fernet = Fernet(key)

        try:
            raw_data = fernet.decrypt(encrypted_data)
        except InvalidToken:
            raise ValueError("Неверный пароль или повреждённые данные")

        # Возвращаем как base64-строку (как в оригинале)
        result_b64 = base64.b64encode(raw_data).decode('ascii')

        # Убираем .enc, если есть
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