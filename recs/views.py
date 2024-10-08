import os
import ast
import json
import pandas as pd

from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.http import HttpResponse
from accounts.views import get_current_theme
from recs.models import RecList, Book, Genre, BookGenre, Location, BookLocation, BookList


def load_recs(request):
    """
    load recs data from .metadata.csv. If the list is not present in the database, it will create a new one and fill it
    with data from data folder.
    """
    directory = os.path.dirname(os.path.realpath(__file__))

    metadata_df = pd.read_csv(directory + '/.metadata.csv')

    for index, row in metadata_df.iterrows():

        list_obj, created = RecList.objects.get_or_create(
            name=row['name'],
            type=row['type'],
            category=row['category'],
        )

        if created:
            filepath = directory + '/data/' + row['filename']

            with open(filepath, 'r') as file:
                lines = file.read().splitlines()

            df_inter = pd.DataFrame(lines)
            df_inter.columns = ['json_element']
            df_inter['json_element'].apply(json.loads)
            df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

            df = df.drop(
                ['titleComplete', 'asin', 'isbn', 'isbn13'],
                axis=1)
            df[['numPages', 'ratingsCount']] = df[['numPages', 'ratingsCount']].fillna(-1)
            df = df.fillna("")

            df['goodreads_id'] = df['url'].str.extract(r'([0-9]+)')

            df['last_uploaded'] = pd.to_datetime('now')

            df = df[['url', 'goodreads_id', 'title', 'description', 'genres', 'author', 'publishDate', 'publisher',
                     'characters', 'ratingsCount', 'reviewsCount', 'numPages', 'places', 'imageUrl',
                     'ratingHistogram', 'language', 'awards', 'series', 'last_uploaded']]

            df = df.astype(
                {'url': 'string', 'goodreads_id': 'Int64', 'title': 'string', 'description': 'string',
                 'genres': 'string',
                 'author': 'string', 'publishDate': 'datetime64[ms]', 'publisher': 'string', 'characters': 'string',
                 'numPages': 'Int64', 'places': 'string', 'imageUrl': 'string', 'ratingHistogram': 'string',
                 'language': 'string', 'awards': 'string', 'series': 'string'})

            for index2, row2 in df.iterrows():
                book_obj = Book(
                    url=row2['url'],
                    goodreads_id=row2['goodreads_id'],
                    title=row2['title'],
                    description=row2['description'],
                    genres=row2['genres'],
                    author=row2['author'],
                    rating_counts=row2['ratingsCount'],
                    number_of_pages=row2['numPages'],
                    places=row2['places'],
                    image_url=row2['imageUrl'],
                )
                book_obj.save()

                booklist_obj = BookList(list_id=list_obj, goodreads_id=book_obj)
                booklist_obj.save()

                if row2['genres']:
                    genres = ast.literal_eval(row2['genres'])

                    for genre_name in genres:
                        genre_obj, created = Genre.objects.get_or_create(name=genre_name)

                        book_genre_obj = BookGenre(goodreads_id=book_obj, genre_id=genre_obj)

                        book_genre_obj.save()

                if row2['places']:
                    places = ast.literal_eval(row2['places'])

                    for place_name in places:
                        place_obj, created = Location.objects.get_or_create(name=place_name)

                        book_location_obj = BookLocation(goodreads_id=book_obj, location_id=place_obj)

                        book_location_obj.save()

    return redirect("recs_main")


def get_metadata_info():
    directory = os.path.dirname(os.path.realpath(__file__))
    metadata_df = pd.read_csv(directory + '/.metadata.csv')
    metadata_df.sort_values(by=['type'], inplace=True)
    metadata_df.reset_index(drop=True, inplace=True)
    return metadata_df


def import_page(request):
    """
    reads the .metadata.csv file and renders a table with the available recs lists.
    """
    metadata = get_metadata_info()
    metadata_df = metadata.to_html(justify='left')
    active_theme = get_current_theme()
    context = {'metadata': metadata_df, 'active_theme': active_theme}

    return render(request, "recs/import_recs.html", context)


def clear_recs(request):
    """
    deletes all objects in the recs app.
    """
    Book.objects.all().delete()
    RecList.objects.all().delete()
    Genre.objects.all().delete()
    Location.objects.all().delete()

    return redirect("import_recs")


def recs_main(request):
    """
    renders the main page of recs. Adds list name on the left sidebar, sorted by category.
    """
    rec_list = RecList.objects.all()
    recs_category = RecList.objects.values('type').distinct().order_by('type')
    active_theme = get_current_theme()

    context = {'rec_list': rec_list, 'rec_cat': recs_category, 'active_theme': active_theme}

    return render(request, "recs/recs.html", context)


def select_list(request):
    """
    gets a list name and returns a list of books belonging to selected list
    """
    name = request.GET.get('listname')

    book_lists = BookList.objects.filter(list_id__name=name).order_by('-goodreads_id__rating_counts')

    # Get books associated with the filtered BookList queryset
    books = [book_list.goodreads_id for book_list in book_lists]
    context = {'books': books, 'reclist_name': name}
    return render(request, 'partials/recs/book_list.html', context)


def rec_detail(request, pk):
    """
    renders a partial containing the book info
    """
    book = get_object_or_404(Book, pk=pk)
    context = {'book': book}

    return render(request, 'partials/recs/rec_detail.html',  context)


def get_genres_count(listname):
    with connection.cursor() as cursor:
        query = """
                SELECT rg.name, COUNT(DISTINCT rb.goodreads_id_id) AS total
                FROM recs_genre rg
                JOIN recs_bookgenre rb ON rg.id = rb.genre_id_id
                JOIN recs_booklist rb2 ON rb.goodreads_id_id = rb2.goodreads_id_id
                JOIN recs_reclist rr ON rb2.list_id_id = rr.id
                WHERE rr.name = %s
                GROUP BY rg.name
                ORDER BY total DESC;
        """
        cursor.execute(query, [listname])
        results = cursor.fetchall()

        return results


def genres_count(request):
    """
    returns a partial containing the genres of the selected list.
    """
    listname = request.GET.get('listname')
    genre_count = get_genres_count(listname)

    context = {'genres': genre_count, 'listname': listname}

    return render(request, 'partials/recs/genres_count.html', context)


def genre_filter(request):
    """
    returns a list of books from the requested list name and genre
    """
    listname = request.GET.get('listname')
    genre = request.GET.get('genre')

    books = Book.objects.filter(booklist__list_id__name=listname, bookgenre__genre_id__name=genre).distinct()
    context = {'books': books, 'reclist_name': listname, 'genre': genre}

    return render(request, 'partials/recs/book_list.html', context)


def get_read_books_id():
    with connection.cursor() as cursor:
        query = """
                select rb.goodreads_id from recs_book rb, books_review br 
                where rb.goodreads_id = br.goodreads_id_id
                and br.bookshelves = 'read'
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def sync_recs(request):
    """
    syncs the user's read shelf with the available recs books by goodreads_id.
    """
    read_books_id = get_read_books_id()
    for book_id_tuple in read_books_id:
        book_id = book_id_tuple[0]
        book = Book.objects.get(goodreads_id=book_id)
        book.read_status = True
        book.save()

    return redirect("recs_main")


def clear_sync(request):
    """
    resets all recs books read_status to false.
    """
    read_books = Book.objects.filter(read_status=True)
    for book in read_books:
        book.read_status = False
        book.save()
    return redirect("recs_main")


def update_read_status(request, pk):
    """
    updates the read_status of a particular book. Useful when encountering a read book with a different goodreads_id.
    (different eddition)
    """
    try:
        book = get_object_or_404(Book, goodreads_id=pk)
        book.read_status = not book.read_status
        book.save()

        return HttpResponse("""<div class="success-message fade-out-message">Updated</div>""")

    except:
        return HttpResponse("""<div class="error-message fade-out-message">Could not update</div>""")
