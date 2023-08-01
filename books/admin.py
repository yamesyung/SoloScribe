from django.contrib import admin
from .models import Book


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "original_publication_year",)

admin.site.register(Book, BookAdmin)
