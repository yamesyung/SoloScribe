from django.urls import path

from .views import book_detail, SearchResultsListView, AuthorListView, AuthorDetailView, timeline, \
    author_graph, ImportView, clear_user_data, clear_scraped_data, ImportAuthorsView, ImportBooksView, book_list_view, \
    book_stats, MapBookView, generate_word_cloud, wordcloud_filter, AuthorMapView, author_graph_3d, \
    get_local_locations_data, book_gallery, export_csv, export_csv_goodreads, export_zip_vault
# htmx urls
from .views import gallery_shelf_filter, gallery_rating_filter, gallery_year_filter, gallery_genre_filter, \
    clear_book_filter, gallery_overlay, search_book, gallery_author_filter, gallery_review_filter, \
    gallery_rating_update, gallery_rating_sidebar_update, gallery_delete_review, gallery_add_review, \
    gallery_review_sidebar_update, gallery_tag_filter, gallery_tag_update, gallery_tag_sidebar_update
# ajax urls
from .views import get_awards_data, get_authors_map_data, get_books_map_data


urlpatterns = [
    path("", book_list_view, name="book_list"),
    path("authors/", AuthorListView.as_view(), name="author_list"),
    path("<int:pk>/", book_detail, name="book_detail"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author_detail"),
    path("search/", SearchResultsListView.as_view(), name="search_results"),
    path("authors/author_timeline/", timeline, name="author_timeline"),
    path("authors/author_graph/", author_graph, name='author_graph'),
    path("authors/author_graph_3d/", author_graph_3d, name='author_graph_3d'),
    path("authors/author_map/", AuthorMapView.as_view(), name='author_map'),
    path("authors/generate_ner/", AuthorMapView.as_view(), name='generate_ner'),
    path("import/", ImportView.as_view(), name='import_csv'),
    path("import/clear_user_data/", clear_user_data, name='clear_user_data'),
    path("import/clear_scraped_data/", clear_scraped_data, name='clear_scraped_data'),
    path("import/authors/", ImportAuthorsView.as_view(), name='import_authors'),
    path("import/books/", ImportBooksView.as_view(), name='import_books'),
    path("export/", export_csv, name='export_csv'),
    path("export/goodreads/", export_csv_goodreads, name='export_csv_goodreads'),
    path("export/obsidian/", export_zip_vault, name='export_zip_vault'),
    path("book_stats/", book_stats, name='book_stats'),
    path("book_map/", MapBookView.as_view(), name='book_map'),
    path("import/local_location/", get_local_locations_data, name='get_local_data'),
    path("import/location/", MapBookView.as_view(), name='get_data'),
    path("word_cloud/", wordcloud_filter, name='wordcloud_filter'),
    path("generate_word_cloud/", generate_word_cloud, name='generate_word_cloud'),
    path("gallery/", book_gallery, name='book_gallery'),
]


htmx_urlpatterns = [
    path("shelf-filter/", gallery_shelf_filter, name='shelf_filter'),
    path("rating-filter/", gallery_rating_filter, name='rating_filter'),
    path("rating-update/<int:pk>/<int:new_rating>", gallery_rating_update, name='rating_update'),
    path("rating-sidebar-update/", gallery_rating_sidebar_update, name='rating_sidebar_update'),
    path("year-filter/", gallery_year_filter, name='year_filter'),
    path("review-filter/", gallery_review_filter, name='review_filter'),
    path("genre-filter/", gallery_genre_filter, name='genre_filter'),
    path("tag-filter/", gallery_tag_filter, name='tag_filter'),
    path("gallery-tag-update/<int:pk>/", gallery_tag_update, name='gallery_tag_update'),
    path("gallery-tag-sidebar-update/", gallery_tag_sidebar_update, name='gallery_tag_sidebar_update'),
    path("gallery-delete-review/<int:pk>/", gallery_delete_review, name='delete_review'),
    path("gallery-add-review/<int:pk>/", gallery_add_review, name='add_review'),
    path("review-sidebar-update/", gallery_review_sidebar_update, name='update_review_count'),
    path("author-filter/", gallery_author_filter, name='author_filter'),
    path("book/<int:pk>/", gallery_overlay, name='gallery_overlay'),
    path("clear_filter/", clear_book_filter, name='clear_filter'),
    path("search-book/", search_book, name='search_book'),
]

ajax_urlpatterns = [
    path("get-awards-data/<int:book_id>/", get_awards_data, name='get_awards_data'),
    path("get-authors-map-data/<str:location>/", get_authors_map_data, name='get_authors_map_data'),
    path("get-books-map-data/<str:location>/", get_books_map_data, name='get_books_map_data'),
]

urlpatterns += htmx_urlpatterns

urlpatterns += ajax_urlpatterns
