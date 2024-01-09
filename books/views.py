import ast

from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.shortcuts import render
from django.db import connection


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
    people_data = Author.objects.filter(birth_date__year__gt=1, death_date__year__gte=1).values('name', 'birth_date', 'death_date')

    for person in people_data:
        person['birth_date'] = Author.convert_date_string(person['birth_date'])
        person['death_date'] = Author.convert_date_string(person['death_date'])

    context = {'people_data': list(people_data) }
    return render(request, "authors/author_timeline.html", context)


def get_author_stats():
    with connection.cursor() as cursor:
        query = """
                select br.author, count(br.author) as books, sum(bb.number_of_pages) as pages from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id
                group by br.author 
                order by pages desc
                limit 20
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def author_stats(request):

    data = get_author_stats()
    context = {'data': list(data)}
    return render(request, "authors/author_stats.html", context)


def author_graph(request):

    data = Author.objects.all().values('name', 'influences')

    for person in data:
        person['influences'] = ast.literal_eval(person['influences'])

    context = {'data': list(data)}
    return render(request, "authors/author_graph.html", context)


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