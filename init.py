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
        allowed_hosts = "127.0.0.1 localhost"

    set_key(".env", "ALLOWED_HOSTS", allowed_hosts)

csrf_trusted_origins = os.getenv("CSRF_TRUSTED_ORIGINS")

if not csrf_trusted_origins:
    print("\nCSRF_TRUSTED_ORIGINS — список доменов, с которых разрешены POST-запросы.")
    print("Нужно если сайт работает за реверс-прокси (nginx) с HTTPS.")
    print("Пример: https://example.com https://www.example.com")
    csrf_trusted_origins = input("Введите доверенные origins (пропуск для локальной разработки): ")

    if not csrf_trusted_origins:
        csrf_trusted_origins = "http://127.0.0.1 http://localhost"

    set_key(".env", "CSRF_TRUSTED_ORIGINS", csrf_trusted_origins)
