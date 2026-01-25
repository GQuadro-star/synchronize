from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from django.utils.crypto import get_random_string
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os

def index_page(request):
    context = {
    "page_name": "Synchronize",
    "menu_items": get_menu_items(),
    }
    return render(request, 'index_page.html', context)

@require_http_methods(['GET', 'POST'])
def upload_file(request):
    if request.method == 'POST':
        uploaded = request.FILES.get('file')
        if not uploaded:
            return JsonResponse({'error': 'Файл не выбран'}, status=400)
        
        # Проверка размера файла
        if uploaded.size > 10485760:  # 10 MB
            return JsonResponse({'error': 'Размер файла превышает 10 МБ'}, status=400)

        safe_name = get_valid_filename(uploaded.name)
        unique_name = f"{get_random_string(8)}_{safe_name}"

        saved_path = default_storage.save(unique_name, uploaded)
        
        file_url = default_storage.url(saved_path)
        download_url = reverse('download_file', kwargs={'filename': unique_name})

        return JsonResponse({
            'saved_path': saved_path, 
            'url': file_url, 
            'filename': unique_name,
            'download_url': download_url
        })
    return redirect(reverse('index'))

def download_file(request, filename):
    file_path = default_storage.path(filename)
    if not default_storage.exists(file_path):
        raise Http404("Файл не найден")
    
    if request.GET.get('download') == 'true':
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    
    file_size = default_storage.size(file_path)
    download_url = f"{reverse('download_file', kwargs={'filename': filename})}?download=true"
    full_url = request.build_absolute_uri(download_url)
    
    context = {
        'filename': filename,
        'file_size': file_size,
        'download_url': download_url,
        'full_url': full_url,
        'page_name': 'Скачать файл',
        'menu_items': get_menu_items(),
    }
    
    return render(request, 'download_page.html', context)

def get_menu_items():
    return [
        {"link": "/", "text": "Synchronize"},
    ]