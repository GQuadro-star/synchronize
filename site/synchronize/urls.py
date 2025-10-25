from django.urls import path
from synchronize import views
urlpatterns = [
    path('',views.index_page),
]
