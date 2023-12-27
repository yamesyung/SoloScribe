import ast
import datetime
from collections import defaultdict

from django.db import models, NotSupportedError
from django.urls import reverse


# Create your models here.
class Book(models.Model):
    url = models.CharField(max_length=200)
    goodreads_id = models.BigIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    author = models.TextField(max_length=300)
    publish_date = models.DateTimeField(null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    characters = models.TextField(null=True, blank=True)
    rating_counts = models.IntegerField(null=True, blank=True)
    review_counts = models.IntegerField(null=True, blank=True)
    number_of_pages = models.IntegerField(null=True, blank=True)
    places = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book_detail", args=[str(self.id)])

    def list_genres(self):
        return self.genres.split("', '")

    def list_characters(self):
        return self.characters.split("', '")

    def list_places(self):
        return self.places.split("', '")


class Review(models.Model):
    goodreads_id = models.BigIntegerField()
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    rating = models.IntegerField()
    original_publication_year = models.IntegerField(null=True, blank=True)
    date_read = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True)
    bookshelves = models.CharField(max_length=200)
    review = models.TextField(null=True, blank=True)
    private_notes = models.TextField(null=True, blank=True)
    read_count = models.IntegerField()
    owned_copies = models.IntegerField()

    def __str__(self):
        return self.review


class Author(models.Model):
    url = models.CharField(max_length=400)
    author_id = models.BigIntegerField()
    name = models.CharField(max_length=200, null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    death_date = models.DateTimeField(null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    influences = models.TextField(null=True, blank=True)
    avg_rating = models.FloatField(null=True, blank=True)
    reviews_count = models.IntegerField(null=True, blank=True)
    rating_count = models.IntegerField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("author_detail", args=[str(self.id)])

    @classmethod
    def convert_date_string(cls, date_string):
        # Ensure date_string is a string
        return date_string.isoformat() if not isinstance(date_string, str) else date_string

    def format_bdate(self):
        if datetime.datetime.strftime(self.birth_date, '%d-%m-%Y') == "01-01-1":
            return ""
        else:
            return datetime.datetime.strftime(self.birth_date, '%d-%m-%Y')

    def format_ddate(self):
        if datetime.datetime.strftime(self.death_date, '%d-%m-%Y') == "01-01-1":
            return ""
        else:
            return datetime.datetime.strftime(self.death_date, '%d-%m-%Y')

    def list_genres(self):
        if self.genres:
            return ast.literal_eval(self.genres)
        else:
            return ""

    @classmethod
    def get_genre_counts(cls, authors):
        # Dictionary to store genre counts
        genre_counts = defaultdict(int)

        # Iterate through authors and update genre counts
        for author in authors:
            # Convert the genres field from string to a list
            genres = ast.literal_eval(author['genres']) if author['genres'] else []

            # Update genre counts
            for genre in genres:
                genre_counts[genre] += 1

        return dict(genre_counts)

    def list_influences(self):
        if self.influences:
            return ast.literal_eval(self.influences)
        else:
            return ""


class OwnedBooksView(models.Model):
    # temporary view to get things sorted with the models relationships
    title = models.CharField(max_length=200, null=True, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    rating_counts = models.IntegerField(null=True, blank=True)
    review_counts = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    number_of_pages = models.IntegerField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    original_publication_year = models.IntegerField(null=True, blank=True)
    characters = models.TextField(null=True, blank=True)
    places = models.TextField(null=True)

    def save(self, *args, **kwargs):
        raise NotSupportedError('This model is tied to a view, it cannot be saved.')

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'owned_books_view'

        # add ordering by date added DESC
