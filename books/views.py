import ast
import json
import pandas as pd
from csv import DictReader
from io import TextIOWrapper
from datetime import datetime


from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.shortcuts import render, redirect
from django.db import connection

from .forms import ImportForm, ReviewForm, BookIdForm, ImportAuthorsForm
from .models import Book, Author, Review


def remove_subset(a):
    return [x for x in a if not any(x in y and x != y for y in a)]


def clear_empty_lists(x):
    if x == ['[', ']']:
        return []
    else:
        return x


def remove_more_suffix(x):
    if x.endswith("...more"):
        return x[:-8]
    else:
        return x


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
                where bb.goodreads_id = br.goodreads_id_id
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


def format_date(date):
    return datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%m-%d')


class ImportView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm()})

    def post(self, request, *args, **kwargs):
        goodreads_file = request.FILES["goodreads_file"]
        rows = TextIOWrapper(goodreads_file, encoding="utf-8", newline="")

        for row in DictReader(rows):
            renamed_row = {
                'goodreads_id': row['Book Id'],
                'title': row['Title'],
                'author': row['Author'],
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
            if renamed_row['date_read']:
                renamed_row['date_read'] = format_date(renamed_row['date_read'])
            renamed_row['date_added'] = format_date(renamed_row['date_added'])

            id_form = BookIdForm(renamed_row)

            if not id_form.is_valid():
                return render(request, "account/import.html", {"form": ImportForm(), "form_errors": id_form.errors})

            id_form.save()

            form = ReviewForm(renamed_row)

            if not form.is_valid():
                return render(request,"account/import.html", {"form": ImportForm(), "form_errors": form.errors})
            form.save()

        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm()})

    # display a success message if the form import succedded
    # add try/catch to add rows


class ImportAuthorsView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm()})

    def post(self, request, *args, **kwargs):
        authors_file = request.FILES["authors_file"]
        lines = authors_file.read().splitlines()
        df_inter = pd.DataFrame(lines)
        df_inter.columns = ['json_element']
        df_inter['json_element'].apply(json.loads)
        df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

        df['author_id'] = df['url'].str.extract(r'([0-9]+)')

        df[['birthDate', 'deathDate']] = df[['birthDate', 'deathDate']].fillna('0001-01-01')
        df[['influences', 'genres']] = df[['influences', 'genres']].fillna('[]')
        df = df.fillna("")

        df['influences'] = df['influences'].apply(remove_subset)
        df['influences'] = df['influences'].apply(clear_empty_lists)

        df = df[['url', 'author_id', 'name', 'birthDate', 'deathDate', 'genres', 'influences', 'avgRating', 'reviewsCount','ratingsCount', 'about']]
        df = df.astype(
            {'url': 'string', 'author_id': 'Int64', 'name': 'string', 'genres': 'string', 'influences': 'string',
             'birthDate': 'string', 'deathDate': 'string', 'reviewsCount': 'Int64', 'ratingsCount': 'Int64',
             'about': 'string'})

        df['about'] = df['about'].apply(remove_more_suffix)

        for index, row in df.iterrows():
            obj = Author(
                url=row['url'],
                author_id=row['author_id'],
                name=row['name'],
                birth_date=row['birthDate'],
                death_date=row['deathDate'],
                genres=row['genres'],
                influences=row['influences'],
                avg_rating=row['avgRating'],
                reviews_count=row['reviewsCount'],
                rating_count=row['ratingsCount'],
                about=row['about']
            )
            obj.save()

        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm()})


def clear_database(request):
    Book.objects.all().delete()
    Review.objects.all().delete()
    Author.objects.all().delete()

    return redirect("import_csv")
