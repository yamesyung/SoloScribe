from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.shortcuts import render
from collections import Counter


from .models import Book, Author


class BookListView(ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/book_list.html"


class AuthorListView(ListView):
    model = Author
    context_object_name = "author_list"
    template_name = "authors/author_list.html"


def timeline(request):
    people_data = Author.objects.filter(birth_date__year__gt=1880,death_date__year__gte=1).values('name', 'birth_date', 'death_date', 'genres')

    for person in people_data:
        person['birth_date'] = Author.convert_date_string(person['birth_date'])
        person['death_date'] = Author.convert_date_string(person['death_date'])

    genre_counts = Author.get_genre_counts(people_data)

    context = {'people_data': list(people_data), 'genre_counts': genre_counts}
    return render(request, "authors/author_timeline.html", context)


class BookDetailView(DetailView):
    model = Book
    context_object_name = "book"
    template_name = "books/book_detail.html"


class AuthorDetailView(DetailView):
    model = Author
    context_object_name = "author"
    template_name = "authors/author_detail.html"


class SearchResultsListView(ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        return Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))