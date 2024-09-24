import os

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from accounts.models import Theme


def get_current_theme():

    current_theme = Theme.objects.filter(active=True).first()
    if current_theme is None:
        return "default"

    return current_theme.name


def themes_page(request):
    theme_dir_path = os.path.join(settings.BASE_DIR, 'static', 'themes')

    try:
        theme_list = [d for d in os.listdir(theme_dir_path) if os.path.isdir(os.path.join(theme_dir_path, d))]
    except FileNotFoundError:
        theme_list = []
    for theme in theme_list:
        Theme.objects.get_or_create(name=theme)

    active_theme = get_current_theme()

    context = {"theme_list": theme_list, "active_theme": active_theme}
    return render(request, "account/themes.html", context)


def change_active_theme(request):
    if request.method == "POST":
        selected_theme = request.POST.get("theme")

    if selected_theme:
        Theme.objects.all().update(active=False)

        theme = get_object_or_404(Theme, name=selected_theme)
        theme.active = True
        theme.save()

    return redirect("themes")
