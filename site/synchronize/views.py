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
            return render(request, 'index_page.html', {
                'error': 'Файл не выбран',
                'page_name': 'Главная'
            })
        # Сохраняем во MEDIA_ROOT если настроен, иначе во временную папку
        save_dir = getattr(settings, 'MEDIA_ROOT', '') or '/tmp'
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, uploaded.name)
        with open(filepath, 'wb+') as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)
        return render(request, 'upload_done.html', {'filename': uploaded.name})
    return redirect(reverse('index'))