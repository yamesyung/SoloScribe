from django.contrib import admin
from .models import Book, Review, Author, Award, Genre, Location


class BookAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id", "title", "author", "publisher",)


admin.site.register(Book, BookAdmin)


class AwardAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id", "name","awarded_at")


admin.site.register(Award, AwardAdmin)


class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Genre, GenreAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "updated")


admin.site.register(Location, LocationAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id_id", "title","author","rating", "date_added", "bookshelves",)


admin.site.register(Review, ReviewAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name","genres","avg_rating","reviews_count","rating_count")


admin.site.register(Author, AuthorAdmin)