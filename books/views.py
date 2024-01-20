import ast
from csv import DictReader
from io import TextIOWrapper
from datetime import datetime

from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.shortcuts import render
from django.db import connection

from .forms import ImportForm, ReviewForm
from .models import Book, Author, Review


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

    author_genres = Author.objects.all().values('genres')
    genres = Author.get_genre_counts(author_genres)

    data = get_author_stats()
    context = {'data': list(data), 'genres': genres}
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


class ImportView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "account/import.html", {"form": ImportForm()})

    def post(self, request, *args, **kwargs):
        review_file = request.FILES["review_file"]
        rows = TextIOWrapper(review_file, encoding="utf-8", newline="")
        default_date = '1970-01-01'
        for row in DictReader(rows):

            renamed_row = {
                'goodreads_id': row['Book Id'],
                'title': row['Title'],
                'author': row['Author'],
                'isbn': row['ISBN'],
                'isbn13': row['ISBN13'],
                'rating': row['My Rating'],
                'year_published': row['Year Published'],
                'original_publication_year': row['Original Publication Year'],
                'date_read': row['Date Read'],
                'date_added': row['Date Added'],
                'bookshelves': row['Exclusive Shelf'],
                'review': row['My Review'],
                'private_notes': row['Private Notes'],
                'read_count': row['Read Count'],
                'owned_copies': row['Owned Copies']
            }

            form = ReviewForm(renamed_row)
            if not form.is_valid():
                return render(request,"account/import.html",{"form": ImportForm(), "form_errors": form.errors})
            form.save()
        return render(request, "account/import.html", {"form": ImportForm()})

    def format_time(self):
        pass
    #format data columns to be compatible with the database