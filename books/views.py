import re
import ast
import json
import spacy
import pandas as pd
from collections import Counter
from csv import DictReader
from io import TextIOWrapper
from html import unescape
from datetime import datetime

from django.views.generic import ListView, DetailView, View
from django.db.models import Q, Value, Count
from django.db.models.functions import Concat, ExtractYear
from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.http import HttpResponse

from .forms import ImportForm, ReviewForm, BookIdForm, ImportAuthorsForm, ImportBooksForm
from .models import Book, Author, Review, Award, Genre, BookGenre, Location, BookLocation, AuthorNER, AuthorLocation, AuthLoc
from geodata.models import Country, City, Region, Place


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


def remove_more_suffix(text):
    """
    function used to remove scraped data: author's description
    it is common to end with '...more'
    """
    if text.endswith("...more"):
        return text[:-8]
    else:
        return text


def remove_duplicate_desc(text):
    """
    function used to clean scraped data: author's description
    it is common to repeat itself after 750 characters OR so
    will remain unused for now
    """
    if len(text) > 751:
        return text[750:]
    else:
        return text


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


def get_author_awards():
    with connection.cursor() as cursor:
        query = """
                SELECT br.author, bb.title, COUNT(baw.goodreads_id_id) AS awards
                FROM books_award baw
                JOIN books_review br ON br.goodreads_id_id = baw.goodreads_id_id
                JOIN books_book bb ON bb.goodreads_id = br.goodreads_id_id
                WHERE br.bookshelves = 'read'
                GROUP BY br.author, bb.title
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_total_pages_count():
    with connection.cursor() as cursor:
        query = """
                select sum(bb.number_of_pages) from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id and br.bookshelves = 'read'
        """
        cursor.execute(query)
        results = cursor.fetchone()

        return results


def author_stats(request):
    """
    function used to render the stats view
    takes data from 3 sources: the SQL queries above
    the limit parameter can be modified to render a different number of results
    the other source is a function which process all authors genres and returns a dict containing the name and the count
    the no. of genres displayed can be modified in the .js file
    """

    author_genres = Author.objects.all().values('genres')
    genres = Author.get_genre_counts(author_genres)

    awards = get_author_awards()
    data = get_author_stats()
    pages_number = get_total_pages_count()

    context = {'data': list(data), 'genres': genres, 'awards': awards, 'pages': pages_number}
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


def author_graph_3d(request):
    """
    function used to render the graph view
    it uses ast to process strings in the form of python lists
    """

    data = Author.objects.all().values('name', 'influences')

    unique_nodes = set()
    nodes = []
    edges = []

    for person in data:
        person['influences'] = ast.literal_eval(person['influences'])

        # Add node for the current author
        author_node_id = f"author_{person['name']}"
        if author_node_id not in unique_nodes:
            nodes.append({"id": author_node_id, "name": person['name']})
            unique_nodes.add(author_node_id)

        # Add nodes for the influenced authors
        for influence_name in person['influences']:
            influence_node_id = f"author_{influence_name}"
            if influence_node_id not in unique_nodes:
                nodes.append({"id": influence_node_id, "name": influence_name})
                unique_nodes.add(influence_node_id)

            # Add edge from the current author to the influenced author
            edges.append({"source": author_node_id, "target": influence_node_id})

    graph_data = {
        "nodes": nodes,
        "links": edges,
    }

    context = {'graph_data': graph_data}
    return render(request, "authors/author_graph_3d.html", context)


class AuthorDetailView(DetailView):
    """
    class used to display author individual page
    get_context_data overridden to get a list of shelved books
    """
    model = Author
    context_object_name = "author"
    template_name = "authors/author_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            query = """
                    select br.goodreads_id_id, br.title, br.original_publication_year, br.bookshelves, br.rating 
                    from books_author ba, books_review br 
                    where ba."name" = br.author and ba."name" = %s
                    order by br.original_publication_year 
            """
            cursor.execute(query, [self.object.name])
            shelved_books = cursor.fetchall()

        context['shelved_books'] = shelved_books

        return context


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
                'additional_authors': row['Additional Authors'],
                'rating': row['My Rating'],
                'year_published': row['Year Published'],
                'original_publication_year': row['Original Publication Year'],
                'date_read': row['Date Read'],
                'date_added': row['Date Added'],
                'bookshelves': row['Exclusive Shelf'],
                'review_content': re.sub(r'<br\s*?/?>', '\n', row['My Review']),
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

        with authors_file.open() as file:
            lines = file.read().splitlines()

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
            try:
                obj.save()
            except:
                obj.birth_date = '0001-01-01'
                obj.save()

        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})


class ImportBooksView(View):
    """
    class used to import the book's .jl file
    it takes file and process it as a dataframe to comply with the model
    it parses the awards column using ast literal_eval and saves the data in the Award model
    does the same for Genres and Location but also adds data to BookGenre and BookLocation
    to manage many-to-many relationships between models
    """
    def get(self, request, *args, **kwargs):
        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})

    def post(self, request, *args, **kwargs):
        books_file = request.FILES["books_file"]

        with books_file.open() as file:
            lines = file.read().splitlines()

        df_inter = pd.DataFrame(lines)
        df_inter.columns = ['json_element']
        df_inter['json_element'].apply(json.loads)
        df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

        df = df.drop(
            ['titleComplete', 'asin', 'isbn', 'isbn13'],
            axis=1)
        df[['numPages', 'publishDate', 'ratingsCount', 'reviewsCount']] = df[['numPages', 'publishDate', 'ratingsCount', 'reviewsCount']].fillna(-1)
        df = df.fillna("")

        df['goodreads_id'] = df['url'].str.extract(r'([0-9]+)')
        df['last_uploaded'] = pd.to_datetime('now')

        df = df[['url', 'goodreads_id', 'title', 'description', 'genres', 'author', 'publishDate', 'publisher',
                 'characters', 'ratingsCount', 'reviewsCount', 'numPages', 'places', 'imageUrl', 'ratingHistogram', 'language', 'awards', 'series', 'last_uploaded']]

        df = df.astype(
            {'url': 'string', 'goodreads_id': 'Int64', 'title': 'string', 'description': 'string', 'genres': 'string',
             'author': 'string', 'publishDate': 'datetime64[ms]', 'publisher': 'string', 'characters': 'string',
             'numPages': 'Int64', 'places': 'string', 'imageUrl': 'string', 'ratingHistogram': 'string',
             'language': 'string', 'awards': 'string', 'series': 'string'})

        for index, row in df.iterrows():
            book_obj = Book(
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
                image_url=row['imageUrl'],
                rating_histogram=row['ratingHistogram'],
                language=row['language'],
                series=row['series'],
                last_uploaded=row['last_uploaded'],
            )
            book_obj.save()

            if row['awards']:
                awards = [(item["name"], item["awardedAt"], item["category"]) for item in ast.literal_eval(row['awards'])]

                for name, awardedAt, category in awards:
                    if awardedAt:
                        try:
                            award_obj = Award(goodreads_id=book_obj, name=name, awarded_at=datetime.utcfromtimestamp(int(awardedAt) / 1000).year, category=category)
                        except:
                            award_obj = Award(goodreads_id=book_obj, name=name, awarded_at=None, category=category)
                    else:
                        award_obj = Award(goodreads_id=book_obj, name=name, awarded_at=None, category=category)

                    award_obj.save()

            if row['genres']:
                genres = ast.literal_eval(row['genres'])

                for genre_name in genres:
                    genre_obj, created = Genre.objects.get_or_create(name=genre_name)

                    book_genre_obj = BookGenre(goodreads_id=book_obj, genre_id=genre_obj)

                    book_genre_obj.save()

            if row['places']:
                places = ast.literal_eval(row['places'])

                for place_name in places:
                    place_obj, created = Location.objects.get_or_create(name=place_name)

                    book_location_obj = BookLocation(goodreads_id=book_obj, location_id=place_obj)

                    book_location_obj.save()

        return render(request, "account/import.html", {"form": ImportForm(), "authors_form": ImportAuthorsForm(), "books_form": ImportBooksForm()})


def clear_database(request):
    """
    function used to apply a database reset, in case of updating the data or testing things
    """
    Review.objects.all().delete()
    Author.objects.all().delete()
    Award.objects.all().delete()
    Genre.objects.all().delete()
    BookGenre.objects.all().delete()
    Location.objects.all().delete()  # keep location data in db
    BookLocation.objects.all().delete()
    Book.objects.all().delete()
    AuthorLocation.objects.all().delete()
    AuthLoc.objects.all().delete()

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


def get_monthly_stats():
    with connection.cursor() as cursor:
        query = """
                select extract ('month' from br.date_read) as "month", count(bb.title) as books, 
                sum(bb.number_of_pages) as pages,
                avg(br.rating) filter (where br.rating > 0)::numeric(10,2) as rating
                from books_review br, books_book bb 
                where bb.goodreads_id = br.goodreads_id_id and 
                br.bookshelves = 'read' and br.date_read is not null
                group by month
                order by month
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_pub_stats():
    with connection.cursor() as cursor:
        query = """
                select bb.title, to_char(br.date_read, 'yyyy') as year_read, 
                to_char(br.date_read, 'yyyy-mm-dd'), br.original_publication_year 
                from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id 
                and br.bookshelves = 'read' and br.date_read notnull
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_yearly_stats():
    with connection.cursor() as cursor:
        query = """
                select coalesce(to_char(br.date_read, 'yyyy'), 'missing date') as year_read, 
                count(bb.title) as books, sum(bb.number_of_pages) as pages
                from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id and br.bookshelves = 'read'
                group by year_read
                order by year_read desc
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_genres_stats():
    with connection.cursor() as cursor:
        query = """
                select bg."name", count(bg."name") as total
                from books_genre bg, books_bookgenre bb, books_review br 
                where br.bookshelves = 'read' and bg."name" not in ('Fiction', 'Nonfiction', 'School', 'Audiobook')
                and bg.id = bb.genre_id_id and br.goodreads_id_id = bb.goodreads_id_id 
                group by bg."name" 
                order by total desc
                limit 15
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_genres_stats_by_year():
    with connection.cursor() as cursor:
        query = """
                WITH ranked_genres AS (
                    SELECT
                        bg."name",
                        coalesce(TO_CHAR(br.date_read, 'yyyy'), 'missing date') AS year,
                        COUNT(bg."name") AS total,
                        ROW_NUMBER() OVER (PARTITION BY coalesce(TO_CHAR(br.date_read, 'yyyy'), 'missing date') ORDER BY COUNT(bg."name") DESC) AS rnk
                    FROM
                        books_genre bg
                    JOIN
                        books_bookgenre bb ON bg.id = bb.genre_id_id
                    JOIN
                        books_review br ON br.goodreads_id_id = bb.goodreads_id_id
                    WHERE
                        br.bookshelves = 'read'
                        AND bg."name" NOT IN ('Fiction', 'Nonfiction', 'School', 'Audiobook')
                    GROUP BY
                        bg."name", year
                )
                SELECT
                    "name",
                    total,
                    year
                FROM
                    ranked_genres
                WHERE
                    rnk <= 10;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_genres_cat():
    with connection.cursor() as cursor:
        query = """
                select bg."name", count(bg."name") as total
                from books_genre bg, books_bookgenre bb, books_review br 
                where br.bookshelves = 'read' and bg."name" in ('Fiction', 'Nonfiction')
                and bg.id = bb.genre_id_id and br.goodreads_id_id = bb.goodreads_id_id 
                group by bg."name" 
                order by total desc
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def book_stats(request):
    """
    function used to retrieve data about books using the queries above
    renders different statistics in one page
    """
    monthly_data = get_monthly_stats()

    pub_stats = get_pub_stats()

    yearly_stats = get_yearly_stats()

    genre_stats = get_genres_stats()
    genre_stats_year = get_genres_stats_by_year()

    genre_category = get_genres_cat()

    context = {'monthlyData': monthly_data, 'pubStats': pub_stats, 'yearStats': yearly_stats, 'genreStats': genre_stats,
               'genreStatsYear': genre_stats_year, 'genreCategory': genre_category}

    return render(request, "books/book_stats.html", context)


def get_book_locations():
    with connection.cursor() as cursor:
        query = """
                select bb.title, br.bookshelves, br.original_publication_year, bl."name", bl.code, bl.latitude, bl.longitude 
                from books_book bb, books_review br, books_location bl, books_booklocation bb2
                where br.bookshelves in ('read', 'to-read') and bl.updated is true and
                bb.goodreads_id = br.goodreads_id_id and bl.id = bb2.location_id_id and bb2.goodreads_id_id = bb.goodreads_id
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_book_locations_stats():
    with connection.cursor() as cursor:
        query = """
                select bl."name", count(bb.goodreads_id_id) as places_count  from books_location bl, books_booklocation bb
                where bl.id = bb.location_id_id and bl.updated = 'True'
                group by bl."name" 
                order by places_count desc
                limit 15
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def update_location(location, location_data):
    if location_data:
        try:
            country_code = location_data.code
            location.code = country_code
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.requested = True
            location.save()
        except:
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.requested = True
            location.save()


def get_local_locations_data(request):
    """
    function that attempts to get location coordinates from local database to reduce the use of geocoding services
    for already popular locations
    it looks for location data in place -> country -> region -> region, country -> city -> city, region -> city, country
    """
    queryset = Location.objects.filter(requested=False)

    if queryset:
        for location in queryset:

            try:
                location_data = Place.objects.get(name=location)
                update_location(location, location_data)
            except Place.DoesNotExist:
                try:
                    location_data = Country.objects.get(name=location)
                    update_location(location, location_data)
                except Country.DoesNotExist:
                    try:
                        location_data = Region.objects.get(Q(region_name=location) | Q(combined_name=location))
                        update_location(location, location_data)
                    except Region.DoesNotExist:
                        try:
                            location_data = City.objects.filter(city_name=location).order_by('-population').first()
                            update_location(location, location_data)
                        except City.DoesNotExist:
                            try:
                                location_data = City.objects.filter(city_name_ascii=location).order_by('-population').first()
                                update_location(location, location_data)
                            except City.DoesNotExist:
                                continue

    queryset_adv = Location.objects.filter(requested=False)

    if queryset_adv:
        for location in queryset_adv:

            try:
                location_query = City.objects.annotate(city_region=Concat('city_name', Value(', '), 'admin_name'))
                location_data = location_query.get(city_region=location)
                update_location(location, location_data)
            except City.DoesNotExist:
                try:
                    location_query = City.objects.annotate(city_region=Concat('city_name', Value(', '), 'country'))
                    location_data = location_query.get(city_region=location)
                    update_location(location, location_data)
                except City.DoesNotExist:
                    location.requested = True
                    location.save()

    return redirect('book_map')


class MapBookView(View):
    def get(self, request, *args, **kwargs):
        """
        queries the db for locations which lack geocoding data (requested = false)
        if empty, set value to 0 and hide Get location data info in js file
        """

        queryset = Location.objects.filter(requested=False)
        empty_loc = len(queryset) or 0
        location_stats = get_book_locations_stats()

        raw_data = get_book_locations()
        locations_data = []

        for item in raw_data:
            location = {
                'title': item[0],
                'status': item[1],
                'year': item[2],
                'location_name': item[3],
                'country_code': item[4],
                'latitude': item[5],
                'longitude': item[6]
            }
            # Handle null values
            for key, value in location.items():
                if value is None:
                    location[key] = 'None'

            locations_data.append(location)

        context = {'emptyLoc': empty_loc, 'queryset': queryset, 'locations': locations_data, 'locations_stats': location_stats}

        return render(request, "books/book_map.html", context)

    def post(self, request, *args, **kwargs):
        """
        queries the OpenStreetMap data for locations which lack geocoding data (requested = false) using Nominatim
        DEPRECATED
        """
        return render(request, "books/book_map.html")


def get_wordcloud_genres():
    with connection.cursor() as cursor:
        query = """
                select bg."name", count(bg."name") as total
                from books_genre bg, books_bookgenre bb, books_book bb2, books_review br 
                where bg."name" not in ('Fiction', 'School', 'Audiobook', 'Nonfiction')
                and bg.id = bb.genre_id_id and bb2.goodreads_id = bb.goodreads_id_id and bb.goodreads_id_id = br.goodreads_id_id 
                and bb2."language" = 'English' and br.bookshelves = 'read'
                group by bg."name" 
                order by total desc
                limit 30
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def wordcloud_filter(request):

    genres = get_wordcloud_genres()
    context = {'genres': genres}

    return render(request, "books/wordcloud_filter.html", context)


def get_book_description_by_genre(language, genre):
    with connection.cursor() as cursor:
        query = """
                select bb.description  from books_book bb, books_bookgenre bb2 , books_genre bg, books_review br 
                where bb.goodreads_id = bb2.goodreads_id_id 
                and bb2.genre_id_id  = bg.id and br.goodreads_id_id = bb2.goodreads_id_id
                and bb."language" = %s and bg."name" = %s and br.bookshelves = 'read'
        """
        cursor.execute(query, [language, genre])
        results = cursor.fetchall()

        return results


def generate_word_cloud(request):

    language = request.GET.get('language', 'English')
    genre = request.GET.get('genre', 'Fiction')

    book_descriptions = get_book_description_by_genre(language, genre)

    nlp = spacy.load("en_core_web_sm")
    stop_words = nlp.Defaults.stop_words
    additional_stopwords = {"year", "novel"}
    stop_words |= additional_stopwords

    word_freqs = Counter()
    for description in book_descriptions:

        cleaned_description = unescape(description[0])
        doc = nlp(cleaned_description)
        tokens = [token.lemma_ for token in doc if token.lemma_.lower() not in stop_words and len(token.text) >= 4 and token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"}]
        word_freqs.update(tokens)

        sorted_word_freqs = dict(sorted(word_freqs.items(), key=lambda x: x[1], reverse=True)[:100])

    context = {'word_freqs': sorted_word_freqs}

    return render(request, "books/book_word_cloud.html", context)


def get_author_locations():
    with connection.cursor() as cursor:
        query = """
                select ba."name", ba2."name" as place, ba2.code, ba2.latitude, ba2.longitude  
                from books_author ba, books_authorlocation ba2, books_authloc ba3
                where ba.author_id = ba3.author_id_id and ba2.id = ba3.authorlocation_id_id and
                ba2.updated is true
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_author_locations_stats():
    with connection.cursor() as cursor:
        query = """
                select ba2."name" , count(authorlocation_id_id) as places_count from books_authloc ba, books_authorlocation ba2 
                where ba.authorlocation_id_id = ba2.id and ba2.updated = 'True'
                group by ba2."name" 
                order by places_count desc
                limit 15
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def update_author_location(location, location_data):
    if location_data:
        try:
            country_code = location_data.code
            location.code = country_code
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.save()
        except:
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.save()


class AuthorMapView(View):
    """
    extract NER data from author's description
    can use loc and person for other ner entities as well
    """
    def get(self, request, *args, **kwargs):

        queryset = Author.objects.filter(processed_ner=False)
        empty_loc = len(queryset) or 0
        location_stats = get_author_locations_stats()

        raw_data = get_author_locations()
        locations_data = []

        for item in raw_data:
            location = {
                'name': item[0],
                'location_name': item[1],
                'country_code': item[2],
                'latitude': item[3],
                'longitude': item[4]
            }
            # Handle null values
            for key, value in location.items():
                if value is None:
                    location[key] = 'None'

            locations_data.append(location)

        context = {'emptyLoc': empty_loc, 'queryset': queryset, 'locations': locations_data,
                   'locations_stats': location_stats}

        return render(request, "authors/author_map.html", context)

    def post(self, request, *args, **kwargs):
        queryset = Author.objects.filter(processed_ner=False)

        if queryset:
            nlp = spacy.load("en_core_web_sm")
            for author in queryset:
                doc = nlp(author.about)

                # Extract entities and convert to list, after storing only unique values
                gpe_list = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "GPE" and all(token.pos_ == "PROPN" for token in ent)))
                loc_list = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "LOC"))
                person_list = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON" and all(token.pos_ == "PROPN" for token in ent)))

                author_ner = AuthorNER.objects.create(
                    author=author,
                    gpe=str(gpe_list),
                    loc=str(loc_list),
                    person=str(person_list)
                )

                author_ner.save()
                # Mark the author as processed
                author.processed_ner = True
                author.save()

                if gpe_list:
                    for location in gpe_list:
                        location_obj, created = AuthorLocation.objects.get_or_create(name=location)
                        try:
                            location_data = Place.objects.get(name=location_obj)
                            update_author_location(location_obj, location_data)
                            author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                            author_loc_obj.save()
                        except Place.DoesNotExist:
                            try:
                                location_data = Country.objects.get(name=location_obj)
                                update_author_location(location_obj, location_data)
                                author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                author_loc_obj.save()
                            except Country.DoesNotExist:
                                try:
                                    location_data = Region.objects.get(Q(region_name=location) | Q(combined_name=location))
                                    update_author_location(location_obj, location_data)
                                    author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                    author_loc_obj.save()
                                except Region.DoesNotExist:
                                    try:
                                        location_data = City.objects.filter(city_name=location_obj).order_by(
                                            '-population').first()
                                        update_author_location(location_obj, location_data)
                                        author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                        author_loc_obj.save()
                                    except City.DoesNotExist:
                                        try:
                                            location_data = City.objects.filter(city_name_ascii=location_obj).order_by(
                                                '-population').first()
                                            update_author_location(location_obj, location_data)
                                            author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                            author_loc_obj.save()
                                        except City.DoesNotExist:
                                            continue

        return redirect("author_map")


def book_gallery(request):

    year_read = Review.objects.filter(bookshelves='read').annotate(year_read=ExtractYear('date_read')).values('year_read').annotate(num_books=Count('id')).order_by('-year_read')
    shelves = Review.objects.values('bookshelves').annotate(num_books=Count('id')).order_by('-num_books')
    genre_counts = Genre.objects.filter(bookgenre__goodreads_id__review__bookshelves__iexact='read').annotate(total=Count('name')).order_by('-total')
    rating_count = Review.objects.filter(bookshelves='read').values('rating').annotate(num_books=Count('id')).order_by('-rating')
    has_review_count = Book.objects.filter(review__bookshelves__iexact='read').exclude(review__review_content__exact='').count()
    no_review_count = Book.objects.filter(review__review_content__exact='', review__bookshelves__iexact='read').count()

    context = {'shelves': shelves, 'year_read': year_read, 'genres': genre_counts, 'ratings': rating_count, 'has_review': has_review_count, 'no_review': no_review_count}

    return render(request, 'books/book_gallery.html', context)


def gallery_shelf_filter(request):
    shelf = request.GET.get('shelf')
    books = Book.objects.filter(review__bookshelves__iexact=shelf).order_by('-review__date_added')[:30]

    context = {'books': books, 'shelf': shelf}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_rating_filter(request):
    rating = request.GET.get('rating')
    books = Book.objects.filter(review__bookshelves__iexact='read', review__rating=rating).order_by('-review__date_added')[:30]

    context = {'books': books, 'rating': rating}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_rating_update(request, pk, new_rating):

    try:
        review = get_object_or_404(Review, goodreads_id=pk)
        review.rating = new_rating
        review.save()

        return HttpResponse("""<div class="success-message fade-out">Updated</div>""")

    except:
        return HttpResponse("""<div class="error-message fade-out">Could not update</div>""")


def gallery_delete_review(request, pk):
    if request.method == 'POST':
        review = get_object_or_404(Review, goodreads_id=pk)
        review.review_content = ""
        review.save()
        return HttpResponse("""<div class="success-message fade-out">Deleting...</div>""")
    else:
        return HttpResponse("""<div class="error-message fade-out">Not deleted</div>""")


def gallery_add_review(request, pk):
    if request.method == 'POST':
        review_content = request.POST.get('review')
        review = get_object_or_404(Review, goodreads_id=pk)
        review.review_content = review_content
        review.save()
        return HttpResponse("""<div class="success-message fade-out">Saving...</div>""")
    else:
        return HttpResponse("""<div class="error-message fade-out">Not saved</div>""")


def gallery_review_sidebar_update(request):
    has_review_count = Book.objects.filter(review__bookshelves__iexact='read').exclude(review__review_content__exact='').count()
    no_review_count = Book.objects.filter(review__review_content__exact='', review__bookshelves__iexact='read').count()
    context = {'has_review': has_review_count, 'no_review': no_review_count}

    return render(request, 'partials/books/gallery_reviews_filter.html', context)


def gallery_rating_sidebar_update(request):

    rating_count = Review.objects.filter(bookshelves='read').values('rating').annotate(num_books=Count('id')).order_by('-rating')
    context = {'ratings': rating_count}

    return render(request, 'partials/books/gallery_ratings.html', context)


def gallery_review_filter(request):
    has_review = request.GET.get('review')
    if has_review.lower() == 'true':
        books = Book.objects.filter(review__bookshelves__iexact='read').exclude(review__review_content__exact='').order_by('-review__date_added')[:30]
    elif has_review.lower() == 'false':
        books = Book.objects.filter(review__review_content__exact='', review__bookshelves__iexact='read').order_by('-review__date_added')[:30]

    context = {'books': books, 'review': has_review}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_year_filter(request):
    year = request.GET.get('year')
    if int(year) > 1:
        books = Book.objects.filter(review__bookshelves__iexact='read', review__date_read__year=year).order_by('-review__date_added')[:30]
    else:
        books = Book.objects.filter(review__bookshelves__iexact='read').filter(review__date_read__year__isnull=True).order_by('-review__date_added')[:30]

    context = {'books': books, 'year': year}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_genre_filter(request):
    genre = request.GET.get('genre')
    books = Book.objects.filter(review__bookshelves__iexact='read', bookgenre__genre_id__name__iexact=genre).order_by('-review__date_added')[:30]

    context = {'books': books, 'genre': genre}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_author_filter(request):
    contributor = request.GET.get('contributor')
    books = Book.objects.filter(author__icontains=contributor).order_by('-review__date_added')[:30]

    context = {'books': books, 'contributor': contributor}

    return render(request, 'partials/books/book_covers.html', context)


def clear_book_filter(request):
    return render(request, 'partials/books/book_covers.html')


def gallery_overlay(request, pk):
    book = get_object_or_404(Book, pk=pk)
    rating_range = range(5, 0, -1)

    context = {'book': book, 'rating_range': rating_range}

    return render(request, 'partials/books/gallery_overlay.html',  context)


def search_book(request):
    search_text = request.POST.get('search')
    books = Book.objects.filter(Q(title__icontains=search_text) | Q(author__icontains=search_text)).order_by('-review__date_added')[:30]

    context = {'books': books, "search_text": search_text}
    return render(request, 'partials/books/book_covers.html', context)

