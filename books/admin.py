from django.contrib import admin
from .models import Book, Review


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher",)

admin.site.register(Book, BookAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id","title","author","rating", "date_added", "bookshelves",)

admin.site.register(Review, ReviewAdmin)