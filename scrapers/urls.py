from django.urls import path

from .views import goodreads_library_scrape, scrape_status_update

urlpatterns = [
    path("start/", goodreads_library_scrape, name="scrape_library"),
    path("status_update/", scrape_status_update, name="scrape_status_update"),
]
