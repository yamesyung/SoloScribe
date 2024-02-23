from django.urls import path

from .views import book_detail, SearchResultsListView, AuthorListView, AuthorDetailView, timeline,\
    author_stats, author_graph, ImportView, clear_database, ImportAuthorsView, ImportBooksView, book_list_view,\
    book_stats, MapBookView, generate_word_cloud, wordcloud_filter, AuthorNERView

urlpatterns = [path("", book_list_view, name="book_list"),
               path("authors/", AuthorListView.as_view(), name="author_list"),
               path("<int:pk>/", book_detail, name="book_detail"),
               path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author_detail"),
               path("search/", SearchResultsListView.as_view(), name="search_results"),
               path("authors/author_timeline/", timeline, name="author_timeline"),
               path("authors/author_stats/", author_stats, name="author_stats"),
               path("authors/author_graph/", author_graph, name='author_graph'),
               path("authors/author_ner/", AuthorNERView.as_view(), name='author_ner'),
               path("authors/generate_ner/", AuthorNERView.as_view(), name='generate_ner'),
               path("import/", ImportView.as_view(), name='import_csv'),
               path("import/clear/", clear_database, name='clear_database'),
               path("import/authors/", ImportAuthorsView.as_view(), name='import_authors'),
               path("import/books/", ImportBooksView.as_view(), name='import_books'),
               path("book_stats/", book_stats, name='book_stats'),
               path("book_map/", MapBookView.as_view(), name='book_map'),
               path("import/location/", MapBookView.as_view(), name='get_data'),
               path("word_cloud/", wordcloud_filter, name='wordcloud_filter'),
               path("generate_word_cloud/", generate_word_cloud, name='generate_word_cloud'),
               ]
