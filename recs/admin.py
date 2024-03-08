from django.contrib import admin
from .models import Book, RecList, Genre, Location


class BookAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id", "title", "author", "places")
    search_fields = ("title", "author")


admin.site.register(Book, BookAdmin)


class RecListAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "category")
    search_fields = ("name", "type", "category")
    list_filter = ("type", "category")


admin.site.register(RecList, RecListAdmin)


class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Genre, GenreAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ["name"]


admin.site.register(Location, LocationAdmin)