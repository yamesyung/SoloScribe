from django.urls import path

from .views import themes_page, change_active_theme, change_cover, change_font, change_text_color

urlpatterns = [
    path("themes/", themes_page, name="themes"),
    path("themes/change/", change_active_theme, name="change_theme"),
    path("cover/change/", change_cover, name="change_cover"),
    path("font/change/", change_font, name="change_font"),
    path("text/change/", change_text_color, name="change_text_color"),
]
