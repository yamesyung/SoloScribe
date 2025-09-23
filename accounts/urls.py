from django.urls import path

from .views import themes_page, change_active_theme, change_cover, change_font, change_text_color, login_page, \
    logout_view, settings_page, change_username, change_password, delete_profile
# htmx views
from .views import create_profile, login_form, profile_settings, change_username_form, change_password_form, \
    delete_profile_form

urlpatterns = [
    path("login-page/", login_page, name="login_page"),
    path("logout/", logout_view, name="logout"),
    path("settings/", settings_page, name="settings"),
    path("change_username/", change_username, name="change_username"),
    path("change_password/", change_password, name="change_password"),
    path("delete_profile/", delete_profile, name="delete_profile"),
    path("themes/", themes_page, name="themes"),
    path("themes/change/", change_active_theme, name="change_theme"),
    path("cover/change/", change_cover, name="change_cover"),
    path("font/change/", change_font, name="change_font"),
    path("text/change/", change_text_color, name="change_text_color"),
]

htmx_urlpatterns = [
    path("create_profile/", create_profile, name="create_profile"),
    path("login_form/", login_form, name="login_form"),
    path("profile_settings/", profile_settings, name="profile_settings"),
    path("change_username_form/", change_username_form, name="change_username_form"),
    path("change_password_form/", change_password_form, name="change_password_form"),
    path("delete_profile_form/", delete_profile_form, name="delete_profile_form"),
]

urlpatterns += htmx_urlpatterns
