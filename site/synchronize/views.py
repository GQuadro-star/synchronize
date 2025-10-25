# import datetime
# import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import JsonResponse


def get_menu_items():
    return [
        {"link": "/", "text": "Synchronize"},
    ]

def index_page(request):
    context = {
    "page_name": "Synchronize",
    "menu_items": get_menu_items(),
    }
    return render(request, "index_page.html", context)