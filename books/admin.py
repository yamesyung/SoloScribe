from django.contrib import admin
from .models import Book, Review, Author, Award, Genre, Location, AuthorNER, AuthorLocation, UserTag, Quote, QuoteTag


class BookAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id", "title", "author", "publisher", "scrape_status")
    search_fields = ("title", "author")


admin.site.register(Book, BookAdmin)


class AwardAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id", "name", "awarded_at")
    search_fields = ["name", "goodreads_id__title"]
    list_filter = ["awarded_at"]


admin.site.register(Award, AwardAdmin)


class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Genre, GenreAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "updated", "requested")
    search_fields = ("name", "code")
    list_filter = ["code"]


admin.site.register(Location, LocationAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "title", "author", "rating", "date_added", "bookshelves")
    search_fields = ("title", "author")
    list_filter = ("bookshelves", "rating")


admin.site.register(Review, ReviewAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "genres", "avg_rating", "reviews_count", "ratings_count", "processed_ner")
    search_fields = ("name", "genres")


admin.site.register(Author, AuthorAdmin)


class AuthorNERAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "gpe", "loc", "person")
    search_fields = ("gpe", "loc", "person")
    ordering = ["author__name"]


admin.site.register(AuthorNER, AuthorNERAdmin)


class AuthorLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "latitude", "longitude", "updated")
    search_fields = ("name", "code")
    list_filter = ["code"]


admin.site.register(AuthorLocation, AuthorLocationAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(UserTag, TagAdmin)


class QuoteAdmin(admin.ModelAdmin):
    list_display = ("review", "get_book", "get_user", "text")
    list_filter = ("review__user", "review__book")

    def get_user(self, obj):
        return obj.review.user

    get_user.admin_order_field = 'review__user'
    get_user.short_description = 'User'

    def get_book(self, obj):
        return obj.review.book

    get_book.admin_order_field = 'review__book'
    get_book.short_description = 'Book'


admin.site.register(Quote, QuoteAdmin)


class QuoteTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(QuoteTag, QuoteTagAdmin)
