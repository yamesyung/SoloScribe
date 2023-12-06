from django.urls import path

from .views import BookListView, BookDetailView, SearchResultsListView, AuthorListView, AuthorDetailView

urlpatterns = [path("", BookListView.as_view(), name="book_list"),
               path("authors/", AuthorListView.as_view(), name="author_list"),
               path("<int:pk>/", BookDetailView.as_view(), name="book_detail"),
               path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author_detail"),
               path("search/", SearchResultsListView.as_view(), name="search_results"),
               ]
