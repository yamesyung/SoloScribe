import os
import re

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models.functions import Lower

from accounts.models import Theme
from .models import CustomUser
from .forms import CustomUserCreationForm


def login_page(request):
    accounts = CustomUser.objects.all().order_by(Lower("username"))
    context = {'accounts': accounts}

    return render(request, 'account/login_page.html', context)


def create_profile(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            response = HttpResponse()
            response['HX-Redirect'] = '/accounts/login-page/'
            return response
    else:
        form = CustomUserCreationForm()

    return render(request, "partials/account/create_user_form.html", {"form": form})


def login_form(request):
    username = request.GET.get("username", "")
    context = {"username": username}

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            response = HttpResponse()
            response['HX-Redirect'] = '/'
            return response
        else:
            return render(request, "partials/account/login_form.html", {
                "username": username,
                "error": "Invalid password"
            })

    return render(request, "partials/account/login_form.html", context)


def logout_view(request):
    logout(request)

    return redirect('login_page')


def get_current_theme():
    """
    gets the current active theme, used when a new full page is rendered
    """
    current_theme = Theme.objects.filter(active=True).first()
    if current_theme is None:
        return "default"

    return current_theme.name


def themes_page(request):
    """
    returns a list of folders from static/themes which contains the static files of the theme (css/js/images/fonts)
    saves the name of new folders in the model, but returns only the current folders
    """
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
    """
    mark as active a selected theme
    """
    if request.method == "POST":
        selected_theme = request.POST.get("theme")

    if selected_theme:
        Theme.objects.all().update(active=False)

        theme = get_object_or_404(Theme, name=selected_theme)
        theme.active = True
        theme.save()

    return redirect("themes")


def change_cover(request):
    """
    save an uploaded image as cover.jpg which will be referred in the base.css
    """
    if request.method == 'POST' and request.FILES.get('background-file'):
        uploaded_file = request.FILES['background-file']
        file_extension = os.path.splitext(uploaded_file.name)[1]

        if file_extension == ".jpg":
            new_filename = f'cover{file_extension}'

            static_dir = os.path.join(settings.BASE_DIR, 'static', 'themes/custom/css')
            file_path = os.path.join(static_dir, new_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            return redirect('themes')
    return redirect('themes')


def change_font(request):
    """
    save an uploaded font as font.ttf which will be referred in the base.css
    """
    if request.method == 'POST' and request.FILES.get('font-file'):
        uploaded_file = request.FILES['font-file']
        file_extension = os.path.splitext(uploaded_file.name)[1]

        if file_extension == ".ttf":
            new_filename = f'font{file_extension}'

            static_dir = os.path.join(settings.BASE_DIR, 'static', 'themes/custom/css')
            file_path = os.path.join(static_dir, new_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            return redirect('themes')
    return redirect('themes')


def change_text_color(request):
    """
    save the color input from the form as a css variable in :root in the base.css
    """
    if request.method == 'POST':
        color = request.POST.get('textColor', '#ff0000')
        css_filepath = os.path.join(settings.BASE_DIR, 'static', 'themes/custom/css/base.css')
        print(color)
        if color != "rgba(0, 0, 0, 0)":  # color picker on linux sends it when it's a null rgb value, happened to me
            try:
                with open(css_filepath, 'r+') as css_file:
                    css_content = css_file.read()

                    updated_content = re.sub(
                        r'(--font-color:\s*)(#[0-9a-fA-F]{6});',
                        rf'\1{color};',
                        css_content
                    )

                    css_file.seek(0)
                    css_file.write(updated_content)
                    css_file.truncate()

            except FileNotFoundError:
                print(f"CSS file not found: {css_filepath}")

            return redirect('themes')
    return redirect('themes')
