from django.urls import path

from .views import goodreads_export_scrape_page, goodreads_library_scrape

urlpatterns = [
    path("", goodreads_export_scrape_page, name="scrape_page"),
    path("start/", goodreads_library_scrape, name="scrape_library"),
]
