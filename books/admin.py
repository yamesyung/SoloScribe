from django.contrib import admin
from .models import Book, Review


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "original_publication_year",)

admin.site.register(Book, BookAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id","rating", "date_added", "bookshelves",)

admin.site.register(Review, ReviewAdmin)