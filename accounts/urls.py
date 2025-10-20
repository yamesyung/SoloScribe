from django.urls import path

from .views import change_active_theme, change_cover, change_font, change_text_color, login_page, \
    logout_view, settings_page, change_username, change_password, delete_profile, import_quotes_csv, \
    import_review_data, export_csv_goodreads, export_quotes_csv, delete_user_data
# htmx views
from .views import create_profile, login_form, profile_settings, change_username_form, change_password_form, \
    delete_profile_form, themes_settings, import_data_settings, export_settings, delete_user_data_form

from books.export_obsidian_vault import export_zip_vault

urlpatterns = [
    path("login-page/", login_page, name="login_page"),
    path("logout/", logout_view, name="logout"),
    path("settings/", settings_page, name="settings"),
    path("change_username/", change_username, name="change_username"),
    path("change_password/", change_password, name="change_password"),
    path("delete_user_data/", delete_user_data, name="delete_user_data"),
    path("delete_profile/", delete_profile, name="delete_profile"),
    path("themes/change/", change_active_theme, name="change_theme"),
    path("cover/change/", change_cover, name="change_cover"),
    path("font/change/", change_font, name="change_font"),
    path("text/change/", change_text_color, name="change_text_color"),
    path("import_review_data/", import_review_data, name='import_review_data'),
    path("import/quotes/", import_quotes_csv, name='import_quotes_csv'),
    path("export/goodreads/", export_csv_goodreads, name='export_csv_goodreads'),
    path("export/obsidian/", export_zip_vault, name='export_zip_vault'),
    path("export/quotes/", export_quotes_csv, name='export_quotes_csv'),
]

htmx_urlpatterns = [
    path("create_profile/", create_profile, name="create_profile"),
    path("login_form/", login_form, name="login_form"),
    path("profile_settings/", profile_settings, name="profile_settings"),
    path("themes_settings/", themes_settings, name="themes_settings"),
    path("import_data_settings/", import_data_settings, name="import_data_settings"),
    path("export_settings/", export_settings, name="export_settings"),
    path("change_username_form/", change_username_form, name="change_username_form"),
    path("change_password_form/", change_password_form, name="change_password_form"),
    path("delete_user_data_form/", delete_user_data_form, name="delete_user_data_form"),
    path("delete_profile_form/", delete_profile_form, name="delete_profile_form"),
]

urlpatterns += htmx_urlpatterns
