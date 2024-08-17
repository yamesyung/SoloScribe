# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from books.models import Book, Genre, BookGenre, Location, BookLocation, Award
import os
import ast
from django.conf import settings
from datetime import datetime


class GrScrapersPipeline(object):
    # to do save book covers locally
    def process_item(self, item, spider):
        filename = f"{item.get('book_id')}.jpg"
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
                rating_counts=item.get('ratingsCount'),
                review_counts=item.get('reviewsCount'),
                number_of_pages=item.get('numPages'),
                places=item.get('places'),
                image_url=item.get('imageUrl'),
                rating_histogram=item.get('ratingHistogram'),
                language=item.get('language'),
                series=item.get('series'),
                scrape_status=True,
                last_updated=datetime.now(),
                cover_local_path=os.path.join('book_covers', filename)
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

            if awards: # to do: save the awards
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


""" 
get covers using requests, not working
           try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Save image to the local directory
                    with open(os.path.join(save_dir, filename), 'wb') as f:
                        f.write(response.content)
                    # Update the cover_local_path for the book
                else:
                    print(f'Failed to fetch {image_url}')

            except Exception as e:
                print(f'Error fetching {image_url}: {str(e)}')

            return item 
"""


