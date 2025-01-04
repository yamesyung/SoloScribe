from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

from scrapyd_api import ScrapydAPI

from books.models import Book, Genre, BookGenre, Location, BookLocation, Award, Author, Review, Quote
from accounts.views import get_current_theme

import requests
import ast
import os
import json
from datetime import datetime
from urllib.parse import urlparse, urlunparse


# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')

book_filepath = os.path.dirname(os.path.realpath(__file__)) + '/gr_scrapers/book_temp_data.json'
author_filepath = os.path.dirname(os.path.realpath(__file__)) + '/gr_scrapers/author_temp_data.json'


def calculate_average_rating(rating_histogram):
    """
    calculate avg rating from the rating histogram returned by book scraper
    used to fill review data
    """
    total_ratings = sum(rating_histogram)
    weighted_sum = sum((i + 1) * count for i, count in enumerate(rating_histogram))
    average_rating = weighted_sum / total_ratings if total_ratings > 0 else 0.0
    return round(average_rating, 2)


def extract_year_publish_date(date_string):
    """
    extract year from a date for the review data
    """
    if not date_string:
        return None

    try:
        date_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return date_object.year
    except ValueError:
        return None


def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError:
        return False

    return True


def clean_url(url):
    """
    Remove the query parameters from a URL.
    """
    parsed_url = urlparse(url)
    cleaned_url = urlunparse(parsed_url._replace(query=''))
    return cleaned_url


def goodreads_library_scrape(request):
    """
    Function which starts a Scrapy crawler command using Scrapyd API.
    It takes the Id's of the books unscraped (scrape_status=False) and sends them to the book's spider,
    where the urls will be processed
    https://www.goodreads.com/book/show/<book_id>

    Can be monitored at: http://localhost:6800/
    """
    books_to_scrape = Book.objects.filter(scrape_status=False)
    book_ids = [str(book.goodreads_id) for book in books_to_scrape]
    if book_ids:
        url = "http://scrapyd:6800/schedule.json"
        data = {
            "project": "default",
            "spider": "book",
            "book_ids": ','.join(book_ids)
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return HttpResponse("""<div id="scraping">Scraping...Please wait</div>""")
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse("No books to scrape")


def scrape_status_update(request):
    """
    Check status of the books scraped.
    Triggered by htmx every 3 seconds
    """
    books_to_scrape_count = Book.objects.filter(scrape_status=False).count()
    context = {"books_to_scrape_count": books_to_scrape_count}

    return render(request, "partials/account/scrape_status_update.html", context)


def check_book_export_status(request):
    """
    function that checks if the book scraper finished exporting the item, in which case it renders the form and book info
    scrapy exports the item in a list, so we need to extract the 1st one before sending to frontend
    triggered by htmx every second after sending the scrapyd request
    """
    filepath = os.path.dirname(os.path.realpath(__file__)) + '/gr_scrapers/book_temp_data.json'
    if os.path.isfile(filepath):
        try:
            if os.path.getsize(filepath) == 0:
                context = {"book": {}, "book_export": False}
                return render(request, 'partials/account/book_temp_data.html', context)
            else:
                with open(filepath, 'r', encoding='utf-8') as file:
                    books = json.load(file)
                    book = books[0] if books else {}
                    context = {"book": book, "book_export": True}

                    return render(request, 'partials/account/book_temp_data.html', context)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        context = {"book_export": False}
        return render(request, 'partials/account/book_temp_data.html', context)


def check_book_export_filepath():
    """
    checks the status of the book temp data file
    based on that, it shows or hide the url input
    """
    filepath = os.path.dirname(os.path.realpath(__file__)) + '/gr_scrapers/book_temp_data.json'
    return os.path.isfile(filepath)


def book_scrape_page(request):
    """
    checks if the book temp data exists before showing the partial containing the save/discard form and book info
    """
    theme = get_current_theme()

    if os.path.isfile(book_filepath):
        try:
            with open(book_filepath, 'r', encoding='utf-8') as file:
                books = json.load(file)
                book = books[0] if books else {}
                context = {"book": book, "book_export": True, "active_theme": theme}
                return render(request, "account/scrape_book.html", context)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    book_export = check_book_export_filepath()
    context = {"active_theme": theme, "book_export": book_export}
    return render(request, "account/scrape_book.html", context)


def save_scraped_book(request):
    """
    save book, author and review based on the JSON data exported by the scrapy spider
    also saves the book cover in the media folder
    for review I tried to fill as many fields as possible to match the Goodreads export file
    """
    bookshelf = request.POST.get('bookshelf')

    if os.path.isfile(book_filepath):
        with open(book_filepath, 'r', encoding='utf-8') as book_file:
            books_data = json.load(book_file)
            for book_data in books_data:
                Book.objects.update_or_create(
                    goodreads_id=book_data['book_id'],
                    defaults={
                        'url': book_data['url'],
                        'title': book_data['title'],
                        'description': book_data['description'],
                        'genres': book_data['genres'],
                        'author': book_data['author'],
                        'quotes_url': book_data.get('quotesUrl', None),
                        'publisher': book_data['publisher'],
                        'publish_date': book_data.get('publishDate', None),
                        'characters': book_data.get('characters', None),
                        'ratings_count': book_data.get('ratingsCount', 0),
                        'reviews_count': book_data.get('reviewsCount', 0),
                        'number_of_pages': book_data.get('numPages', 0),
                        'places': book_data.get('places', None),
                        'image_url': book_data.get('imageUrl', None),
                        'rating_histogram': book_data.get('ratingHistogram', None),
                        'language': book_data.get('language', None),
                        'series': book_data.get('series', None),
                        'scrape_status': True,
                        'last_updated': datetime.now(),
                    },
                )

                save_dir = os.path.join(settings.MEDIA_ROOT, 'book_covers')
                image_url = book_data.get('imageUrl')
                genres = book_data.get('genres')
                places = book_data.get('places')
                awards = book_data.get('awards')
                book = Book.objects.get(goodreads_id=book_data['book_id'])

                if genres:
                    genres_list = ast.literal_eval(str(genres))
                    for genre_name in genres_list:
                        genre_obj, created = Genre.objects.get_or_create(name=genre_name)

                        book_genre_obj, created = BookGenre.objects.get_or_create(goodreads_id=book, genre_id=genre_obj)

                if places:
                    places_list = ast.literal_eval(str(places))
                    for place_name in places_list:
                        place_obj, created = Location.objects.get_or_create(name=place_name)

                        book_location_obj, created = BookLocation.objects.get_or_create(goodreads_id=book,
                                                                                        location_id=place_obj)

                if awards:
                    awards_list = [(item["name"], item["awardedAt"], item["category"]) for item in
                                   ast.literal_eval(str(awards))]
                    for name, awardedAt, category in awards_list:
                        if awardedAt:
                            try:
                                awarded_at = (
                                    datetime.utcfromtimestamp(int(awardedAt) / 1000).year
                                    if awardedAt else None
                                )

                                award_obj, created = Award.objects.get_or_create(
                                    goodreads_id=book,
                                    name=name,
                                    awarded_at=awarded_at,
                                    category=category
                                )

                            except Exception as e:
                                print(f"Error processing award {name}: {e}")

                filename = f"{book.goodreads_id}.jpg"
                file_path = os.path.join(save_dir, filename)

                if os.path.isfile(file_path):

                    book.cover_local_path = os.path.join('book_covers', filename)
                    book.save()

                else:
                    if image_url:
                        try:
                            response = requests.get(image_url)
                            if response.status_code == 200:
                                with open(os.path.join(save_dir, filename), 'wb') as f:
                                    f.write(response.content)

                                book.cover_local_path = os.path.join('book_covers', filename)
                                book.save()
                            else:
                                print(f'Failed to fetch {image_url}')

                        except Exception as e:
                            print(f"Error downloading or saving image: {e}")

                if os.path.isfile(author_filepath):
                    with open(author_filepath, 'r', encoding='utf-8') as author_file:
                        author_data = json.load(author_file)
                        Author.objects.update_or_create(
                            author_id=author_data['author_id'],
                            defaults={
                                    'url': author_data['url'],
                                    'name': author_data['name'],
                                    'birth_date': author_data['birth_date'],
                                    'death_date': author_data['death_date'],
                                    'genres': author_data['genres'],
                                    'influences': author_data['influences'],
                                    'avg_rating': author_data['avg_rating'],
                                    'reviews_count': author_data['reviews_count'],
                                    'ratings_count': author_data['ratings_count'],
                                    'about': author_data['about'],
                                    },
                        )

                        review = Review.objects.update_or_create(
                            id=book_data['book_id'],
                            defaults={
                                'goodreads_id_id': book_data['book_id'],
                                'title': book_data['titleComplete'],
                                'author': author_data['name'],
                                'isbn': book_data.get('isbn', None),
                                'isbn13': book_data.get('isbn13', None),
                                'publisher': book_data.get('publisher', None),
                                'number_of_pages': book_data.get('numPages', None),
                                'year_published': extract_year_publish_date(book_data['publishDate']),
                                'original_publication_year': extract_year_publish_date(book_data.get('firstPublished', None)),
                                'date_added': datetime.now(),
                                'bookshelves': bookshelf,
                                'binding': book_data.get('format'),
                                'rating': 0,
                                'review_content': None,
                                'average_rating': calculate_average_rating(book_data['ratingHistogram']),
                                'read_count': 0,
                                'owned_copies': 0
                            }
                        )

    if os.path.isfile(book_filepath):
        os.remove(book_filepath)
    if os.path.isfile(author_filepath):
        os.remove(author_filepath)

    return redirect("book_scrape_page")


def discard_scraped_book(request):
    """
    check if the temporary files exists and deletes them, refreshing the page
    """
    if os.path.isfile(book_filepath):
        os.remove(book_filepath)
    if os.path.isfile(author_filepath):
        os.remove(author_filepath)

    return redirect("book_scrape_page")


def scrape_single_book_url(request):
    """
    sends a request to scrapy with the book url
    """
    if request.method == "POST":
        if os.path.isfile(book_filepath):
            os.remove(book_filepath)
        if os.path.isfile(author_filepath):
            os.remove(author_filepath)

        book_url = request.POST.get('url')
        cleaned_url = clean_url(book_url)

        url = "http://scrapyd:6800/schedule.json"
        data = {
            "project": "default",
            "spider": "book_preview",
            "book_url": cleaned_url,
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

        return HttpResponse(cleaned_url)

    return HttpResponse("ok")


def scrape_quotes_url(request, pk):
    """
    sends a request to scrapy with the quotes url, saving first 2 pages (max 60 quotes)
    """
    if request.method == "POST":
        book = get_object_or_404(Book, goodreads_id=pk)
        if not book.scraped_quotes:
            context = {"book": book}

            url = "http://scrapyd:6800/schedule.json"
            data = {
                "project": "default",
                "spider": "goodreads_quotes",
                "book_id": book.goodreads_id,
                "quotes_url": book.quotes_url,
            }

            try:
                response = requests.post(url, data=data)
                response.raise_for_status()
            except requests.RequestException as e:
                return JsonResponse({"error": str(e)}, status=500)

            return render(request, "partials/books/book_detail/quotes_status.html", context)

        return HttpResponse("already scraped")
    return HttpResponse("bad request")


def quotes_status_update(request, pk):
    """
    Check status of the quotes scraped.
    Triggered by htmx every second
    """
    book = get_object_or_404(Book, pk=pk)

    context = {"book": book}
    return render(request, "partials/books/book_detail/quotes_status.html", context)
