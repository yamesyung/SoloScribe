import ast
import json
import pandas as pd
from csv import DictReader
from io import TextIOWrapper
from datetime import datetime

from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection

from .forms import ImportForm, ReviewForm, BookIdForm, ImportAuthorsForm, ImportBooksForm
from .models import Book, Author, Review


def remove_subset(a):
    """
    function used to clean scraped data: author's influences
    it is common it contains substrings of author's name
    """
    return [x for x in a if not any(x in y and x != y for y in a)]


def clear_empty_lists(x):
    """
    function used to clean scraped data: author's list
    I want list data type to be stored in the database as a string with a python list form,
    so I can process it later using abstract syntax trees
    """
    if x == ['[', ']']:
        return []
    else:
        return x


def remove_more_suffix(x):
    """
    function used to remove scraped data: author's description
    it is common to end with '...more'
    """
    if x.endswith("...more"):
        return x[:-8]
    else:
        return x


def format_date(date):
    """
    function used to process date fields when importing the csv file
    """
    return datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%m-%d')


class AuthorListView(ListView):
    """
    class used to display a table containing all authors
    """
    model = Author
    context_object_name = "author_list"
    template_name = "authors/author_list.html"


def timeline(request):
    """
    function used to render the timeline view
    It filters authors with unknown birthdate(0001-01-01)
    treats the authors with unknown death date(0001-01-01) as currently alive in the .js file
    need testing with negative values
    """
    people_data = Author.objects.filter(birth_date__year__gt=1).values('name', 'birth_date', 'death_date')

    for person in people_data:
        person['birth_date'] = Author.convert_date_string(person['birth_date'])
        person['death_date'] = Author.convert_date_string(person['death_date'])

    context = {'people_data': list(people_data) }
    return render(request, "authors/author_timeline.html", context)


def get_author_stats():
    with connection.cursor() as cursor:
        query = """
                select br.author, count(br.author) as books, sum(bb.number_of_pages) as pages from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id and br.bookshelves = 'read'
                group by br.author 
                order by pages desc
                limit 20
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def author_stats(request):
    """
    function used to render the stats view
    takes data from 2 sources: the SQL query above returning name, book count and no of pages in the read bookshelf
    the limit parameter can be modified to render a different number of results
    the 2nd source is a function which process all authors genres and returns a dict containing the name and the count
    the no. of genres displayed can be modified in the .js file
    """

    author_genres = Author.objects.all().values('genres')
    genres = Author.get_genre_counts(author_genres)

    data = get_author_stats()
    context = {'data': list(data), 'genres': genres}
    return render(request, "authors/author_stats.html", context)


def author_graph(request):
    """
    function used to render the graph view
    it uses ast to process strings in the form of python lists
    optional: filter data by read/to-read authors; add option to exclude authors with no influences
    """

    data = Author.objects.all().values('name', 'influences')

    for person in data:
        person['influences'] = ast.literal_eval(person['influences'])

    context = {'data': list(data)}
    return render(request, "authors/author_graph.html", context)


class AuthorDetailView(DetailView):
    """
    class used to display author individual page
    """
    model = Author
    context_object_name = "author"
    template_name = "authors/author_detail.html"


class SearchResultsListView(ListView):
    """
    not modified since tutorial
    """
    model = Book
    context_object_name = "book_list"
    template_name = "books/search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        return Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))


class ImportView(View):
    """
    class used to import goodreads user's data
    it takes the csv and it applies a series of transformations to comply with the model
    It creates the book object with the correspondent Id before saving the review
    """

    def get(self, request, *args, **kwargs):
        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})

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
                return render(request, "account/import.html", {"form": ImportForm(), "form_errors": id_form.errors, "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})

            id_form.save()

            form = ReviewForm(renamed_row)

            if not form.is_valid():
                return render(request, "account/import.html", {"form": ImportForm(), "form_errors": form.errors, "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})
            form.save()

        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})

    # display a success message if the form import succeeded
    # add try/catch to add rows


class ImportAuthorsView(View):
    """
    class used to import the author's .jl file
    it takes file and process it as a dataframe to comply with the model
    """
    def get(self, request, *args, **kwargs):
        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})

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

        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})


class ImportBooksView(View):
    """
    class used to import the book's .jl file
    it takes file and process it as a dataframe to comply with the model
    """
    def get(self, request, *args, **kwargs):
        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})

    def post(self, request, *args, **kwargs):
        books_file = request.FILES["books_file"]
        lines = books_file.read().splitlines()
        df_inter = pd.DataFrame(lines)
        df_inter.columns = ['json_element']
        df_inter['json_element'].apply(json.loads)
        df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

        df = df.drop(
            ['titleComplete', 'imageUrl', 'asin', 'isbn', 'isbn13', 'series', 'ratingHistogram', 'language', 'awards'],
            axis=1)
        df[['numPages', 'publishDate']] = df[['numPages', 'publishDate']].fillna(-1)
        df = df.fillna("")

        df['goodreads_id'] = df['url'].str.extract(r'([0-9]+)')
        df = df[['url', 'goodreads_id', 'title', 'description', 'genres', 'author', 'publishDate', 'publisher',
                 'characters', 'ratingsCount', 'reviewsCount', 'numPages', 'places']]

        df = df.astype(
            {'url': 'string', 'goodreads_id': 'Int64', 'title': 'string', 'description': 'string', 'genres': 'string',
             'author': 'string', 'publishDate': 'datetime64[ms]', 'publisher': 'string', 'characters': 'string',
             'numPages': 'Int64', 'places': 'string'})

        for index, row in df.iterrows():
            obj = Book(
                url=row['url'],
                goodreads_id=row['goodreads_id'],
                title=row['title'],
                description=row['description'],
                genres=row['genres'],
                author=row['author'],
                publish_date=row['publishDate'],
                publisher=row['publisher'],
                characters=row['characters'],
                rating_counts=row['ratingsCount'],
                review_counts=row['reviewsCount'],
                number_of_pages=row['numPages'],
                places=row['places'],
            )
            obj.save()

        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})


def clear_database(request):
    """
    function used to apply a database reset, in case of updating the data or testing things
    """
    Book.objects.all().delete()
    Review.objects.all().delete()
    Author.objects.all().delete()

    return redirect("import_csv")


def get_book_list():
    with connection.cursor() as cursor:
        query = """
                select bb.title, br.author, br.rating, br.bookshelves, bb.number_of_pages, br.original_publication_year,
                bb.goodreads_id, ba.author_id, TO_CHAR(br.date_read, 'dd-mm-yyyy'), TO_CHAR(br.date_added, 'dd-mm-yyyy')
                from books_author ba, books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id and br.author = ba."name"
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def book_list_view(request):
    """
    function used to display a table containing all imported books
    it uses the above SQL query to get data from all 3 tables, using joins
    """

    book_list = get_book_list()
    context = {'book_list': list(book_list)}

    return render(request, "books/book_list.html", context)


def get_book_detail(pk):
    with connection.cursor() as cursor:
        query = """
                select ba.author_id, br.id, br.author, br.rating, br.bookshelves, TO_CHAR(br.date_read, 'dd-mm-yyyy'),
                br.original_publication_year, br.review from books_author ba, books_review br
                where br.author = ba."name" and br.goodreads_id_id =  %s
        """
        cursor.execute(query, [pk])
        result = cursor.fetchone()

        return result


def book_detail(request, pk):
    """
    function used to display book detail page.
    It uses the book model and the above query
    """
    review = get_book_detail(pk)
    book = get_object_or_404(Book, pk=pk)

    context = {'review': review, 'book': book}

    return render(request, "books/book_detail.html", context)
