from django.db import models

# Create your models here.
class Book(models.Model):
    goodreads_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    number_of_pages = models.IntegerField(null=True)
    year_published = models.IntegerField(null=True)
    original_publication_year = models.IntegerField(null=True)

    def __str__(self):
        return self.title