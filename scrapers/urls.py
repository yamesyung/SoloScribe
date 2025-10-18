from django.urls import path

from .views import goodreads_library_scrape, scrape_status_update, book_scrape_page, scrape_single_book_url, \
     save_scraped_book, discard_scraped_book, check_book_export_status, scrape_quotes_url, quotes_status_update

urlpatterns = [
    path("start/", goodreads_library_scrape, name="scrape_library"),
    path("book_scrape_page/", book_scrape_page, name="book_scrape_page"),
]

htmx_urlpatterns = [
    path("status_update/", scrape_status_update, name="scrape_status_update"),
    path("scrape_single_book_url/", scrape_single_book_url, name="scrape_single_book_url"),
    path("check_book_export_status/", check_book_export_status, name="check_book_export_status"),
    path("save_scraped_book/", save_scraped_book, name="save_scraped_book"),
    path("discard_scraped_book/", discard_scraped_book, name="discard_scraped_book"),
    path("scrape_quotes_url/<int:review_id>", scrape_quotes_url, name="scrape_quotes_url"),
    path("quotes_status_update/<int:review_id>", quotes_status_update, name="quotes_status_update"),
]

urlpatterns += htmx_urlpatterns
