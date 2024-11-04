# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from books.models import Book, Genre, BookGenre, Location, BookLocation, Award
import os
import ast
import requests
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
        try:
            book = Book(
                url=item.get('url'),
                goodreads_id=item.get('book_id'),
                title=item.get('title'),
                description=item.get('description'),
                genres=item.get('genres'),
                author=item.get('author'),
                publisher=item.get('publisher'),
                publish_date=item.get('publishDate'),
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

                    book_genre_obj = BookGenre(goodreads_id=book, genre_id=genre_obj)

                    book_genre_obj.save()

            if places:
                places_list = ast.literal_eval(str(places))
                for place_name in places_list:
                    place_obj, created = Location.objects.get_or_create(name=place_name)

                    book_location_obj = BookLocation(goodreads_id=book, location_id=place_obj)

                    book_location_obj.save()

            if awards:
                awards_list = [(item["name"], item["awardedAt"], item["category"]) for item in ast.literal_eval(str(awards))]
                for name, awardedAt, category in awards_list:
                    if awardedAt:
                        try:
                            award_obj = Award(goodreads_id=book, name=name, awarded_at=datetime.utcfromtimestamp(int(awardedAt) / 1000).year, category=category)
                        except:
                            award_obj = Award(goodreads_id=book, name=name, awarded_at=None, category=category)
                    else:
                        award_obj = Award(goodreads_id=book, name=name, awarded_at=None, category=category)

                    award_obj.save()

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
