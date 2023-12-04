from django.contrib import admin
from .models import Book, Review, Author, OwnedBooksView


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher",)

admin.site.register(Book, BookAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id","title","author","rating", "date_added", "bookshelves",)

admin.site.register(Review, ReviewAdmin)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name","genres","avg_rating","reviews_count","rating_count")

admin.site.register(Author, AuthorAdmin)