from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from scrapyd_api import ScrapydAPI

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

