from django.urls import path
from synchronize import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('upload/', views.upload_file, name='upload'),
]