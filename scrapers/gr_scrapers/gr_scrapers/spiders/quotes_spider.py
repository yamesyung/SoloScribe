import scrapy
from ..items import QuoteItem, QuoteLoader
from books.models import Book


class GoodReadsQuotesSpider(scrapy.Spider):
    """
    Extract quotes from a /work/quotes/ type page on Goodreads
    limit to the first 2 pages
    """
    name = 'goodreads_quotes'
    custom_settings = {
        'ITEM_PIPELINES': {
            'gr_scrapers.pipelines.GoodreadsQuotesPipeline': 401,
        }
    }

    def __init__(self, book_id=None, quotes_url=None, *args, **kwargs):
        super(GoodReadsQuotesSpider, self).__init__(*args, **kwargs)
        self.book_id = book_id
        self.quotes_url = quotes_url
        self.page_count = 0

    def start_requests(self):
        url = self.quotes_url

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, loader=None):
        self.page_count += 1

        for quote in response.xpath("//div[@class='quote']"):
            loader = QuoteLoader(item=QuoteItem(), selector=quote, response=response)
            loader.add_value('book_id', self.book_id)
            loader.add_xpath('text', ".//div[@class='quoteText']/text()[1]")
            loader.add_xpath('author', ".//div[@class='quoteText']/span[1]")
            loader.add_xpath('tags', ".//div[@class='greyText smallText left']/a")
            yield loader.load_item()

        next_page = response.selector.xpath("//a[@class='next_page']/@href").extract_first()
        if next_page is not None and self.page_count < 2:
            next_page_link = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_link, callback=self.parse)

        Book.objects.filter(goodreads_id=self.book_id).update(scraped_quotes=True)
