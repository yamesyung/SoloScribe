from django.urls import path

from .views import themes_page, change_active_theme, change_cover, change_font, change_text_color, login_page, \
    logout_view
# htmx views
from .views import create_profile, login_form

urlpatterns = [
    path("login-page/", login_page, name="login_page"),
    path("logout/", logout_view, name="logout"),
    path("themes/", themes_page, name="themes"),
    path("themes/change/", change_active_theme, name="change_theme"),
    path("cover/change/", change_cover, name="change_cover"),
    path("font/change/", change_font, name="change_font"),
    path("text/change/", change_text_color, name="change_text_color"),
]

htmx_urlpatterns = [
    path("create_profile/", create_profile, name="create_profile"),
    path("login_form/", login_form, name="login_form"),
]

urlpatterns += htmx_urlpatterns
