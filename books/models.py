import ast
import datetime
from collections import defaultdict

from django.db import models
from django.urls import reverse


# Create your models here.
class Book(models.Model):
    url = models.CharField(max_length=200)
    goodreads_id = models.BigIntegerField(primary_key=True)
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
    image_url = models.CharField(max_length=300, null=True, blank=True)
    cover_local_path = models.CharField(max_length=300, null=True, blank=True)
    rating_histogram = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True)
    series = models.CharField(max_length=500, null=True, blank=True)
    scrape_status = models.BooleanField(default=False)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book_detail", args=[str(self.goodreads_id)])

    def list_authors(self):
        if self.author:
            return ast.literal_eval(self.author)
        else:
            return ""

    def list_genres(self):
        if self.genres:
            return ast.literal_eval(self.genres)
        else:
            return ""

    def list_characters(self):
        if self.characters:
            return ast.literal_eval(self.characters)
        else:
            return ""

    def list_places(self):
        if self.places:
            return ast.literal_eval(self.places)
        else:
            return ""

    def list_series(self):
        if self.series:
            return ast.literal_eval(self.series)
        else:
            return ""

    def format_publish_date(self):
        if datetime.datetime.strftime(self.publish_date, '%d-%m-%Y') == "01-01-1":
            return ""
        else:
            return datetime.datetime.strftime(self.publish_date, '%d-%m-%Y')


class Award(models.Model):
    goodreads_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    awarded_at = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BookGenre(models.Model):
    goodreads_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE)


class Location(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    updated = models.BooleanField(default=False)
    requested = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BookLocation(models.Model):
    goodreads_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)


class Review(models.Model):
    goodreads_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    additional_authors = models.TextField(null=True, blank=True)
    isbn = models.CharField(max_length=50, null=True, blank=True)
    isbn13 = models.CharField(max_length=50, null=True, blank=True)
    rating = models.IntegerField()
    year_published = models.IntegerField(null=True, blank=True)
    original_publication_year = models.IntegerField(null=True, blank=True)
    date_read = models.DateField(null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)
    bookshelves = models.CharField(max_length=200)
    review_content = models.TextField(null=True, blank=True)
    private_notes = models.TextField(null=True, blank=True)
    read_count = models.IntegerField()
    owned_copies = models.IntegerField()

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        return self.review_content


class Author(models.Model):
    url = models.CharField(max_length=400)
    author_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    birth_date = models.DateTimeField(null=True, blank=True)
    death_date = models.DateTimeField(null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    influences = models.TextField(null=True, blank=True)
    avg_rating = models.FloatField(null=True, blank=True)
    reviews_count = models.IntegerField(null=True, blank=True)
    rating_count = models.IntegerField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    processed_ner = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("author_detail", args=[str(self.author_id)])

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


class AuthorNER(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    gpe = models.TextField(null=True, blank=True)
    loc = models.TextField(null=True, blank=True)
    person = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.author)


class AuthorLocation(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    updated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class AuthLoc(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)
    authorlocation_id = models.ForeignKey(AuthorLocation, on_delete=models.CASCADE)

