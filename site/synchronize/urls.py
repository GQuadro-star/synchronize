from django.urls import path
from synchronize import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index_page, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)