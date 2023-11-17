from django.db import models

# Create your models here.
class Book(models.Model):
    goodreads_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    number_of_pages = models.IntegerField(null=True)
    year_published = models.IntegerField(null=True)
    original_publication_year = models.IntegerField(null=True)
    description = models.TextField(null=True)
    last_updated = models.DateTimeField(null=True)


    def __str__(self):
        return self.title


class Review(models.Model):
    goodreads_id = models.BigIntegerField()
    title = models.CharField(max_length=200, null=True)
    author = models.CharField(max_length=200, null=True)
    rating = models.IntegerField()
    date_read = models.DateTimeField(null=True)
    date_added = models.DateTimeField(null=True)
    bookshelves = models.CharField(max_length=200)
    review = models.TextField(null=True)
    private_notes = models.TextField(null=True)
    read_count = models.IntegerField()
    owned_copies = models.IntegerField()

    def __str__(self):
        return self.review