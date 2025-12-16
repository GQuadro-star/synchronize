import os
import secrets
import json
from dotenv import load_dotenv, set_key

load_dotenv()

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    secret_key = input("Секретный ключ не был обнаружен. Введите его (пропуск для автоматической генерации): ")

    if not secret_key:
        secret_key = secrets.token_urlsafe(50)
    
    set_key(".env", "SECRET_KEY", secret_key)

allowed_hosts = os.getenv("ALLOWED_HOSTS")

if not allowed_hosts:
    allowed_hosts = input("Введите разрешённые хосты (пропуск для пустого списка): ")
    
    if not allowed_hosts:
        allowed_hosts = "[]"
    else:
        allowed_hosts = json.dumps(allowed_hosts.split())
    set_key(".env", "ALLOWED_HOSTS", allowed_hosts)
