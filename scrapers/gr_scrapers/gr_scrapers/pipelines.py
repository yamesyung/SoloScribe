# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from books.models import Book, Genre, BookGenre, Location, BookLocation, Award, Quote, QuoteTag, QuoteQuoteTag
import os
import ast
import requests
from scrapy.exporters import JsonItemExporter
from scrapy.exceptions import DropItem
from django.conf import settings
from datetime import datetime


class GrScrapersPipeline(object):
    """
    The main pipeline for scraping books. I've decided to process the author data in the book spider for simplicity.
    It saves book data in the local database, as well as additional info, like genres, locations and awards
    It also saves book covers in the media/book_covers directory, after checking if the file doesn't already exists,
    to reduce the number of requests
    """
    def process_item(self, item, spider):
        save_dir = os.path.join(settings.MEDIA_ROOT, 'book_covers')
        image_url = item.get('imageUrl')
        genres = item.get('genres')
        places = item.get('places')
        awards = item.get('awards')

        if not item.get('title'):
            book = Book(goodreads_id=item.get('book_id'), scrape_status=True)
            book.save()
            raise DropItem("Missing data for item")

        try:
            book = Book(
                url=item.get('url'),
                goodreads_id=item.get('book_id'),
                title=item.get('title'),
                description=item.get('description'),
                genres=item.get('genres'),
                author_text=item.get('author'),
                publisher=item.get('publisher'),
                publish_date=item.get('publishDate'),
                quotes_url=item.get('quotesUrl'),
                characters=item.get('characters'),
                ratings_count=item.get('ratingsCount'),
                reviews_count=item.get('reviewsCount'),
                number_of_pages=item.get('numPages'),
                places=item.get('places'),
                image_url=item.get('imageUrl'),
                rating_histogram=item.get('ratingHistogram'),
                language=item.get('language'),
                series=item.get('series'),
                scrape_status=True,
                last_updated=datetime.now()
            )
            book.save()

            if genres:
                genres_list = ast.literal_eval(str(genres))
                for genre_name in genres_list:
                    genre_obj, created = Genre.objects.get_or_create(name=genre_name)

                    book_genre_obj, created = BookGenre.objects.get_or_create(goodreads_id=book, genre_id=genre_obj)

            if places:
                places_list = ast.literal_eval(str(places))
                for place_name in places_list:
                    place_obj, created = Location.objects.get_or_create(name=place_name)

                    book_location_obj, created = BookLocation.objects.get_or_create(goodreads_id=book, location_id=place_obj)

            if awards:
                awards_list = [(item["name"], item["awardedAt"], item["category"]) for item in ast.literal_eval(str(awards))]
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

        except Exception as error:
            print("An exception occurred:", error)

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


class BookTempDataPipeline(object):
    def open_spider(self, spider):

        self.file = open('book_temp_data.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):

        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):

        self.exporter.export_item(item)
        return item


class GoodreadsQuotesPipeline(object):

    def process_item(self, item, spider):
        book_id = item.get('book_id')
        book = Book.objects.get(goodreads_id=book_id)
        quote_tags = item.get('tags')

        quote = Quote(
            book=book,
            text=item.get('text')
        )
        quote.save()

        if quote_tags:
            tag_list = ast.literal_eval(str(quote_tags))
            for tag_name in tag_list:
                tag_obj, created = QuoteTag.objects.get_or_create(name=tag_name)

                quote_tag_obj, created = QuoteQuoteTag.objects.get_or_create(quote_id=quote, tag_id=tag_obj)

