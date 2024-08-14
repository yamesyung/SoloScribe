
from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
from .models import Quote
from books.models import Book
import requests

# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')


def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True


def goodreads_export_scrape_page(request):
    """
    main scraping page for goodreads library export file
    """
    return render(request, "scrapers/goodreads_export_scrape.html")


def goodreads_library_scrape(request):

    books_to_scrape = Book.objects.all()  # add proper filter for unscraped books
    book_ids = [str(book.goodreads_id) for book in books_to_scrape]

    url = "http://scrapyd:6800/schedule.json"
    data = {
        "project": "default",
        "spider": "book",
        "book_ids": ','.join(book_ids)
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return JsonResponse(response.json())
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

