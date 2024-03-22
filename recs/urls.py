from django.urls import path
from .views import clear_recs, import_page, load_recs, recs_main

from .views import select_list, rec_detail, genres_count, genre_filter

urlpatterns = [
    path("import/clear/", clear_recs, name="clear_recs"),
    path("import/", import_page, name="import_recs"),
    path("import/recs/", load_recs, name="load_recs"),
    path("", recs_main, name="recs_main"),
]

htmx_urlpatterns = [
    path("list/", select_list, name="recs_list"),
    path("book/<int:pk>/", rec_detail, name="rec_detail"),
    path("genres_count/", genres_count, name="genres_count"),
    path("list/filter/", genre_filter, name="genre_filter"),

]

urlpatterns += htmx_urlpatterns
