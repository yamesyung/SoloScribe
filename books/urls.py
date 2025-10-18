from django.urls import path

from .views import book_detail, search_results, author_list, author_detail, timeline, \
    author_graph, clear_user_data, clear_scraped_data, book_list, \
    book_stats, book_world_page, generate_word_cloud, wordcloud_filter, AuthorMapView, author_graph_3d, \
    get_local_locations_data, book_gallery, export_csv, export_csv_goodreads, remove_book, \
    quotes_page, delete_book_quotes, export_quotes_csv, delete_all_quotes, delete_author, \
    save_book_edit

from .export_obsidian_vault import export_zip_vault
# htmx urls
from .views import gallery_shelf_filter, gallery_rating_filter, gallery_year_filter, gallery_genre_filter, \
    clear_book_filter, gallery_overlay, search_book, gallery_author_filter, gallery_review_filter, \
    gallery_rating_update, gallery_rating_sidebar_update, gallery_delete_review, gallery_add_review, \
    gallery_review_sidebar_update, gallery_tag_filter, gallery_tag_update, gallery_tag_sidebar_update, \
    gallery_date_read_update, gallery_year_sidebar_update, gallery_shelf_update, gallery_shelf_sidebar_update, \
    book_detail_quotes, favorite_quote, delete_quote, edit_quote, save_edited_quote, save_new_quote, new_quote_form, \
    update_quote_count, review_form, save_review, quotes_tag_filter, quotes_favorite_filter, \
    quotes_update_fav_sidebar, quotes_update_tags_sidebar, quotes_page_search, quotes_book_filter, \
    quotes_update_books_sidebar, edit_book_form
# ajax urls
from .views import get_awards_data, get_authors_map_data, get_books_map_data


urlpatterns = [
    path("", book_list, name="book_list"),
    path("authors/", author_list, name="author_list"),
    path("<int:pk>/", book_detail, name="book_detail"),
    path("save_book_edit/<int:review_id>/", save_book_edit, name="save_book_edit"),
    path("remove_book/<int:review_id>/", remove_book, name="remove_book"),
    path("delete-book-quotes/<int:review_id>/", delete_book_quotes, name="delete_book_quotes"),
    path("authors/<int:pk>/", author_detail, name="author_detail"),
    path("delete-author/<int:author_id>/", delete_author, name='delete_author'),
    path("search/", search_results, name="search_results"),
    path("authors/author_timeline/", timeline, name="author_timeline"),
    path("authors/author_graph/", author_graph, name='author_graph'),
    path("authors/author_graph_3d/", author_graph_3d, name='author_graph_3d'),
    path("authors/author_map/", AuthorMapView.as_view(), name='author_map'),
    path("authors/generate_ner/", AuthorMapView.as_view(), name='generate_ner'),
    path("import/clear_user_data/", clear_user_data, name='clear_user_data'),
    path("import/delete-all-quotes/", delete_all_quotes, name='delete_all_quotes'),
    path("import/clear_scraped_data/", clear_scraped_data, name='clear_scraped_data'),
    path("export/", export_csv, name='export_csv'),
    path("export/goodreads/", export_csv_goodreads, name='export_csv_goodreads'),
    path("export/obsidian/", export_zip_vault, name='export_zip_vault'),
    path("book_stats/", book_stats, name='book_stats'),
    path("book_map/", book_world_page, name='book_map'),
    path("import/local_location/", get_local_locations_data, name='get_local_data'),
    path("word_cloud/", wordcloud_filter, name='wordcloud_filter'),
    path("generate_word_cloud/", generate_word_cloud, name='generate_word_cloud'),
    path("gallery/", book_gallery, name='book_gallery'),
    path("quotes-page/", quotes_page, name='quotes_page'),
    path("export/quotes/", export_quotes_csv, name='export_quotes_csv'),
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
    path("gallery_date_read_update/<int:pk>/", gallery_date_read_update, name='gallery_date_read_update'),
    path("gallery-year-sidebar-update/", gallery_year_sidebar_update, name='gallery_year_sidebar_update'),
    path("gallery-shelf-update/<int:pk>/", gallery_shelf_update, name='gallery_shelf_update'),
    path("gallery-shelf-sidebar-update/", gallery_shelf_sidebar_update, name='gallery_shelf_sidebar_update'),
    path("gallery-delete-review/<int:pk>/", gallery_delete_review, name='delete_review'),
    path("gallery-add-review/<int:pk>/", gallery_add_review, name='add_review'),
    path("review-sidebar-update/", gallery_review_sidebar_update, name='update_review_count'),
    path("author-filter/", gallery_author_filter, name='author_filter'),
    path("book/<int:pk>/", gallery_overlay, name='gallery_overlay'),
    path("clear_filter/", clear_book_filter, name='clear_filter'),
    path("search-book/", search_book, name='search_book'),
    path("book-detail-quotes/<int:pk>", book_detail_quotes, name='book_detail_quotes'),
    path("edit-book-form/<int:review_id>", edit_book_form, name='edit_book_form'),
    path("book-favorite-quote/<int:quote_id>", favorite_quote, name='favorite_quote'),
    path("book-delete-quote/<int:quote_id>", delete_quote, name='delete_quote'),
    path("book-edit-quote/<int:quote_id>", edit_quote, name='edit_quote'),
    path("save-edited-quote/<int:quote_id>", save_edited_quote, name='save_edited_quote'),
    path("new-quote-form/<int:review_id>", new_quote_form, name='new_quote_form'),
    path("save-new-quote/<int:review_id>", save_new_quote, name='save_new_quote'),
    path("update-quote-count/<int:review_id>", update_quote_count, name='update_quote_count'),
    path("review-form/<int:review_id>", review_form, name='review_form'),
    path("save-review/<int:review_id>", save_review, name='save_review'),
    path("quotes-tag-filter/", quotes_tag_filter, name='quotes_tag_filter'),
    path("quotes-update-tags-sidebar/", quotes_update_tags_sidebar, name='quotes_update_tags_sidebar'),
    path("quotes-update-books-sidebar/", quotes_update_books_sidebar, name='quotes_update_books_sidebar'),
    path("quotes-fav-filter/", quotes_favorite_filter, name='quotes_favorite_filter'),
    path("quotes-book-filter/<int:book_id>", quotes_book_filter, name='quotes_book_filter'),
    path("quotes-update-fav-sidebar/", quotes_update_fav_sidebar, name='quotes_update_fav_sidebar'),
    path("quotes-search/", quotes_page_search, name='quotes_page_search'),
]

ajax_urlpatterns = [
    path("get-awards-data/<int:book_id>/", get_awards_data, name='get_awards_data'),
    path("get-authors-map-data/<str:location>/", get_authors_map_data, name='get_authors_map_data'),
    path("get-books-map-data/<str:location>/", get_books_map_data, name='get_books_map_data'),
]

urlpatterns += htmx_urlpatterns

urlpatterns += ajax_urlpatterns
