
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os

def index_page(request):
    return render(request, 'index_page.html', {'page_name': 'Главная'})

@require_http_methods(['GET', 'POST'])
def upload_file(request):
    if request.method == 'POST':
        uploaded = request.FILES.get('file')
        if not uploaded:
            return JsonResponse({'error': 'Файл не выбран'}, status=400)

        # безопасное имя файла
        safe_name = get_valid_filename(uploaded.name)
        # добавим префикс, чтобы уменьшить шанс перезаписи
        unique_name = f"{get_random_string(8)}_{safe_name}"

        # Сохраняем через default_storage — по умолчанию это FileSystemStorage, корневой путь берётся из MEDIA_ROOT
        saved_path = default_storage.save(unique_name, uploaded)
        # saved_path — относительный путь внутри storage (например 'a1b2c3_file.wav')
        # Чтобы получить URL (в dev - /media/...), используем default_storage.url
        file_url = default_storage.url(saved_path)

        # Вернём результат (JSON) или редирект/рендер шаблона — как вам удобнее
        return JsonResponse({'saved_path': saved_path, 'url': file_url, 'filename': unique_name})
    return redirect(reverse('index'))