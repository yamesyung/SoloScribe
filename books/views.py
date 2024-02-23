import ast
import json
import spacy
import pandas as pd
from collections import Counter
from csv import DictReader
from io import TextIOWrapper
from html import unescape
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection

from .forms import ImportForm, ReviewForm, BookIdForm, ImportAuthorsForm, ImportBooksForm
from .models import Book, Author, Review, Award, Genre, BookGenre, Location, BookLocation, AuthorNER


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
                'additional_authors': row['Additional Authors'],
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
        df[['numPages', 'publishDate']] = df[['numPages', 'publishDate']].fillna(-1)
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
                        award_obj = Award(goodreads_id=book_obj, name=name, awarded_at=datetime.utcfromtimestamp(int(awardedAt) / 1000).year, category=category)
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
    # Location.objects.all().delete() #keep location data in db
    BookLocation.objects.all().delete()
    Book.objects.all().delete()

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

    genre_category = get_genres_cat()

    context = {'monthlyData': monthly_data, 'pubStats': pub_stats, 'yearStats': yearly_stats, 'genreStats': genre_stats, 'genreCategory': genre_category}

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


class MapBookView(View):
    def get(self, request, *args, **kwargs):
        """
        queries the db for locations which lack geocoding data (requested = false)
        if empty, set value to 0 and hide Get location data info in js file
        """

        queryset = Location.objects.filter(requested=False)
        empty_loc = len(queryset) or 0

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

        context = {'emptyLoc': empty_loc, 'queryset': queryset, 'locations': locations_data}

        return render(request, "books/book_map.html", context)

    def post(self, request, *args, **kwargs):
        """
        queries the db for locations which lack geocoding data (requested = false)
        but, requested can be set to true when no data was given: no results found or nominatim related problems
        it gets trickier with Max retries exceeded error, so I added a rate limiter and keep the data in db
        (it remains when clearing the db via clear db button)
        if need of reset, un-comment line from clear_databases and clear database
        """

        queryset = Location.objects.filter(requested=False)
        empty_loc = len(queryset) or 0

        if queryset:
            geolocator = Nominatim(user_agent="book-stats")
            geocode_with_rate = RateLimiter(geolocator.geocode, max_retries=3, min_delay_seconds=1)

            for location in queryset:

                location_data = geocode_with_rate(location, exactly_one=True, language="en", addressdetails=True)

                if location_data:
                    # Update the Location model instance with fetched data
                    country_code = location_data.raw['address'].get('country_code', None)

                    if country_code:
                        location.code = country_code

                    location.latitude = location_data.latitude
                    location.longitude = location_data.longitude
                    location.updated = True
                    location.requested = True
                    location.save()

                else:
                    location.requested = True
                    location.save()

        context = {'emptyLoc': empty_loc, 'queryset': queryset}

        return render(request, "books/book_map.html", context)


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


class AuthorNERView(View):
    """
    extract NER data from author's description !!!EXPERIMENTAL!!!
    Maybe translate first to English from other languages
    to be continued
    """
    def get(self, request, *args, **kwargs):
        return render(request, "authors/author_ner.html")

    def post(self, request, *args, **kwargs):
        queryset = Author.objects.filter(processed_ner=False)

        if queryset:
            nlp = spacy.load("en_core_web_sm")
            for author in queryset:
                doc = nlp(author.about)

                # Extract entities and convert to list, after storing only unique values
                gpe_tuple = list(set(ent.text for ent in doc.ents if ent.label_ == "GPE"))
                loc_tuple = list(set(ent.text for ent in doc.ents if ent.label_ == "LOC"))
                person_tuple = list(set(ent.text for ent in doc.ents if ent.label_ == "PERSON"))

                author_ner = AuthorNER.objects.create(
                    author=author,
                    gpe=str(gpe_tuple),
                    loc=str(loc_tuple),
                    person=str(person_tuple)
                )

                author_ner.save()
                # Mark the author as processed
                author.processed_ner = True
                author.save()

        return render(request, "authors/author_ner.html")
