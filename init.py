import os
import secrets
from dotenv import load_dotenv, set_key

load_dotenv()

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    secret_key = input("Секретный ключ не был обнаружен. Введите его (пропуск для автоматической генерации): ")

    if not secret_key:
        secret_key = secrets.token_urlsafe(50)
    
    set_key(".env", "SECRET_KEY", secret_key)