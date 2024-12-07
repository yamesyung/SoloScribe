from django.urls import path

from .views import themes_page, change_active_theme

urlpatterns = [
    path("themes/", themes_page, name="themes"),
    path("themes/change/", change_active_theme, name="change_theme"),
]
