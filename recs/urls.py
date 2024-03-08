from django.urls import path

from .views import clear_recs, import_page, load_recs

urlpatterns = [
    path("import/clear/", clear_recs, name="clear_recs"),
    path("import/", import_page, name="import_recs"),
    path("import/recs/", load_recs, name="load_recs"),
               ]
