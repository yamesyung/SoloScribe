from django.urls import path

from .views import goodreads_library_scrape

urlpatterns = [
    path("start/", goodreads_library_scrape, name="scrape_library"),
]
