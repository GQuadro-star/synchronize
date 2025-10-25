from django.shortcuts import render

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