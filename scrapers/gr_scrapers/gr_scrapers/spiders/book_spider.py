"""Spider to extract information from a /book/show type page on Goodreads"""

import scrapy
import re
from datetime import datetime
from books.views import remove_subset, remove_more_suffix, clean_author_description

from ..items import BookItem, BookLoader, AuthorItem, AuthorLoader
from books.models import Author, Book


def safe_date(value):
    """Validate and convert date strings to safe ISO format."""
    if not value:
        return "0001-01-01"
    try:
        value = value.strip().replace("“", "").replace("”", "")
        for fmt in ("%B %d, %Y", "%Y-%m-%d", "%Y/%m/%d", "%b %d, %Y"):
            try:
                dt = datetime.strptime(value, fmt)
                # Avoid weird years like 2055 instead of 0055
                if dt.year < 1000:
                    raise ValueError("Year too early")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
    except Exception:
        pass

    return "0001-01-01"


class BookSpider(scrapy.Spider):
    """
    Extract information from a /book/show type page on Goodreads
    """
    name = "book"
    base_url = "https://www.goodreads.com/book/show/"
    custom_settings = {
        'ITEM_PIPELINES': {
            'gr_scrapers.pipelines.GrScrapersPipeline': 300,
        }
    }

    def __init__(self, book_ids=None, *args, **kwargs):
        super(BookSpider, self).__init__(*args, **kwargs)
        if book_ids:
            self.book_ids = book_ids.split(',')  # Split the comma-separated string into a list of IDs
        else:
            self.book_ids = []

        self.logger.info(f"Initialized BookSpider with book_ids: {self.book_ids}")

    def start_requests(self):
        if not self.book_ids:
            self.logger.error("No book IDs provided")
            return
        for book_id in self.book_ids:
            url = f"{self.base_url}{book_id}"
            self.logger.info(f"Generating request for URL: {url}")
            yield scrapy.Request(url, meta={'book_id': book_id}, callback=self.parse)

    def parse(self, response, loader=None):

        if not loader:
            loader = BookLoader(BookItem(), response=response)

        loader.add_value('url', response.request.url)
        loader.add_value('book_id', response.meta['book_id'])
        loader.add_css('author_url', 'script#__NEXT_DATA__::text')

        loader.add_css('title', 'script#__NEXT_DATA__::text')
        loader.add_css('titleComplete', 'script#__NEXT_DATA__::text')
        loader.add_css('description', 'script#__NEXT_DATA__::text')
        loader.add_css('imageUrl', 'script#__NEXT_DATA__::text')
        loader.add_css('genres', 'script#__NEXT_DATA__::text')
        loader.add_css('asin', 'script#__NEXT_DATA__::text')
        loader.add_css('isbn', 'script#__NEXT_DATA__::text')
        loader.add_css('isbn13', 'script#__NEXT_DATA__::text')
        loader.add_css('publisher', 'script#__NEXT_DATA__::text')
        loader.add_css('series', 'script#__NEXT_DATA__::text')
        loader.add_css('author', 'script#__NEXT_DATA__::text')
        loader.add_css('publishDate', 'script#__NEXT_DATA__::text')
        loader.add_css('quotesUrl', 'script#__NEXT_DATA__::text')
        loader.add_css('characters', 'script#__NEXT_DATA__::text')
        loader.add_css('places', 'script#__NEXT_DATA__::text')
        loader.add_css('ratingHistogram', 'script#__NEXT_DATA__::text')
        loader.add_css("ratingsCount", 'script#__NEXT_DATA__::text')
        loader.add_css("reviewsCount", 'script#__NEXT_DATA__::text')
        loader.add_css('numPages', 'script#__NEXT_DATA__::text')
        loader.add_css("format", 'script#__NEXT_DATA__::text')

        loader.add_css('language', 'script#__NEXT_DATA__::text')
        loader.add_css("awards", 'script#__NEXT_DATA__::text')

        yield loader.load_item()

        author_url = loader.get_output_value('author_url')
        book_id = loader.get_output_value('book_id')
        author_id_match = re.search(r'/author/show/(\d+)', author_url)

        if author_id_match:
            author_id = author_id_match.group(1)
            author, created = Author.objects.get_or_create(author_id=author_id)
            if created:
                yield response.follow(author_url, callback=self.parse_author, cb_kwargs={'book_id': book_id})
            else:
                try:
                    book = Book.objects.get(goodreads_id=book_id)
                    book.author = author
                    book.save()

                except Exception as e:
                    self.log(f"Error saving author to book: {e}")

    def parse_author(self, response, book_id):
        loader = AuthorLoader(AuthorItem(), response=response)
        loader.add_value('url', response.request.url)
        loader.add_css("name", 'h1.authorName>span[itemprop="name"]::text')
        loader.add_css("birthDate", 'div.dataItem[itemprop="birthDate"]::text')
        loader.add_css("deathDate", 'div.dataItem[itemprop="deathDate"]::text')
        loader.add_css("genres", 'div.dataItem>a[href*="/genres/"]::text')
        loader.add_css("influences", 'div.dataItem>span>a[href*="/author/show"]::text')
        loader.add_css("avgRating", 'span.average[itemprop="ratingValue"]::text')
        loader.add_css("reviewsCount", 'span[itemprop="reviewCount"]::attr(content)')
        loader.add_css("ratingsCount", 'span[itemprop="ratingCount"]::attr(content)')
        loader.add_css("about", 'div.aboutAuthorInfo')

        author_item = loader.load_item()

        # Access individual fields from the loaded item
        author_url = author_item.get('url')
        author_name = author_item.get('name')
        birth_date = safe_date(author_item.get("birthDate"))
        death_date = safe_date(author_item.get("deathDate"))

        genres = loader.get_output_value('genres')
        influences = loader.get_output_value('influences')

        if influences:
            influences = remove_subset(influences)

        avg_rating = author_item.get('avgRating')
        reviews_count = author_item.get('reviewsCount')
        ratings_count = author_item.get('ratingsCount')
        about = clean_author_description(remove_more_suffix(author_item.get('about', '')))

        author_id_match = re.search(r'/author/show/(\d+)', author_url)
        author_id = author_id_match.group(1)

        author = Author(
            author_id=author_id,
            url=author_url,
            name=author_name,
            birth_date=birth_date,
            death_date=death_date,
            genres=genres,
            influences=influences,
            avg_rating=avg_rating,
            reviews_count=reviews_count,
            ratings_count=ratings_count,
            about=about
        )
        author.save()

        try:
            book = Book.objects.get(goodreads_id=book_id)
            book.author = author
            book.save()

        except Exception as e:
            self.log(f"Error saving author to book: {e}")
