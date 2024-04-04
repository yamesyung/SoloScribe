import ast

from django.db import models


class RecList(models.Model):
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=200)
    category = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    goodreads_id = models.BigIntegerField(primary_key=True)
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    author = models.TextField(max_length=300)
    rating_counts = models.IntegerField(null=True, blank=True)
    number_of_pages = models.IntegerField(null=True, blank=True)
    places = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=300, null=True, blank=True)
    read_status = models.BooleanField(default=False)

    class Meta:
        ordering = ["-rating_counts"]

    def __str__(self):
        return self.title

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


class BookList(models.Model):
    list_id = models.ForeignKey(RecList, on_delete=models.CASCADE)
    goodreads_id = models.ForeignKey(Book, on_delete=models.CASCADE)


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

    def __str__(self):
        return self.name


class BookLocation(models.Model):
    goodreads_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
